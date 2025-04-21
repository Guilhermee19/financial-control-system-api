import base64
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.models import Transaction
from core.serializers import TransactionSerializer


class TransactionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Listar transações com filtros por data, tipo, status, conta e categoria.",
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Data inicial (YYYY-MM-DD)", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="Data final (YYYY-MM-DD)", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('account', openapi.IN_QUERY, description="ID da conta", type=openapi.TYPE_INTEGER),
            openapi.Parameter('category', openapi.IN_QUERY, description="ID da categoria", type=openapi.TYPE_INTEGER),
            openapi.Parameter('type', openapi.IN_QUERY, description="Tipo da transação (INCOME ou EXPENDITURE)", type=openapi.TYPE_STRING),
            openapi.Parameter('status', openapi.IN_QUERY, description="Status (true para pagas, false para não pagas)", type=openapi.TYPE_STRING),
            openapi.Parameter('recurrence', openapi.IN_QUERY, description="Recorrência (SINGLE, INSTALLMENTS, etc)", type=openapi.TYPE_STRING),
            openapi.Parameter('order_by', openapi.IN_QUERY, description="Campo para ordenar (ex: expiry_date)", type=openapi.TYPE_STRING),
            openapi.Parameter('order_direction', openapi.IN_QUERY, description="Direção da ordenação (asc ou desc)", type=openapi.TYPE_STRING),
        ]
    )
    def list(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not start_date or not end_date:
            return Response({"error": "start_date and end_date are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return Response({"error": "Invalid date format, use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

        filters = {
            'expiry_date__gte': start_date,
            'expiry_date__lte': end_date,
            'created_by': request.user
        }

        # Filtros adicionais
        for field in ['account', 'category', 'recurrence', 'type']:
            value = request.GET.get(field)
            if value:
                filters[field] = value

        status_param = request.GET.get('status')
        if status_param is not None:
            filters['is_paid'] = status_param.lower() == 'true'

        queryset = Transaction.objects.filter(**filters)

        # Ordenação
        order_by = request.GET.get('order_by', 'expiry_date')
        order_direction = request.GET.get('order_direction', 'asc')
        if order_by not in ['description', 'account', 'category', 'value', 'is_paid', 'expiry_date']:
            order_by = 'expiry_date'
        queryset = queryset.order_by(f'-{order_by}' if order_direction == 'desc' else order_by)

        serializer = TransactionSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        transaction = get_object_or_404(Transaction, id=pk)
        return Response(TransactionSerializer(transaction).data)

    def create(self, request):
        user = request.user
        data = request.data.copy()
        installments = int(data.get('installments', 1))
        recurrence = data.get('recurrence', 'SINGLE')
        total_value = float(data.get('value', 0))

        data['created_by'] = user.id
        data['updated_by'] = user.id
        value_installment = total_value / installments if recurrence == 'INSTALLMENTS' and installments > 0 else total_value
        data['value_installment'] = value_installment

        serializer = TransactionSerializer(data=data)
        if serializer.is_valid():
            transaction = serializer.save(installments=installments, related_transaction=None)
            base_expiry_date = transaction.expiry_date
            transaction_group = transaction.pk

            for i in range(1, installments):
                if recurrence == 'INSTALLMENTS':
                    new_expiry = base_expiry_date + relativedelta(months=i)
                elif recurrence == 'WEEKLY':
                    new_expiry = base_expiry_date + timedelta(weeks=i)
                elif recurrence == 'MONTHLY':
                    new_expiry = base_expiry_date + relativedelta(months=i)
                elif recurrence == 'ANNUAL':
                    new_expiry = base_expiry_date + relativedelta(years=i)
                else:
                    new_expiry = base_expiry_date

                Transaction.objects.create(
                    value=transaction.value,
                    value_installment=value_installment,
                    description=transaction.description,
                    account=transaction.account,
                    category=transaction.category,
                    expiry_date=new_expiry,
                    is_paid=False,
                    date_payment=None,
                    receipt=None,
                    current_installment=i+1,
                    installments=installments,
                    related_transaction=transaction,
                    type=transaction.type,
                    recurrence=recurrence,
                    created_by=user,
                    updated_by=user
                )

            return Response({"transaction_group": str(transaction_group)}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        transaction = get_object_or_404(Transaction, id=pk)
        data = request.data
        edit_all = data.get('edit_all', False)

        if edit_all:
            installments = int(data.get('installments', transaction.installments))
            recurrence = data.get('recurrence', transaction.recurrence)
            total_value = float(data.get('value', transaction.value))
            value_installment = total_value / installments if recurrence == 'INSTALLMENTS' else total_value
            data['value_installment'] = value_installment

        serializer = TransactionSerializer(transaction, data=data, partial=True)
        if serializer.is_valid():
            updated = serializer.save()

            if edit_all:
                related_set = Transaction.objects.filter(
                    related_transaction=updated.related_transaction or updated,
                    expiry_date__gte=updated.expiry_date
                )
                for rel in related_set:
                    rel.value_installment = updated.value / updated.installments
                    rel.value = updated.value
                    rel.description = updated.description
                    rel.account_id = data.get('account', rel.account_id)
                    rel.category_id = data.get('category', rel.category_id)
                    rel.save()

            return Response({
                "message": "Transaction updated successfully.",
                "transaction": TransactionSerializer(updated).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        transaction = get_object_or_404(Transaction, id=pk)
        all_related = request.query_params.get('all_transaction', 'false').lower() == 'true'

        if all_related:
            if transaction.related_transaction is None:
                Transaction.objects.filter(related_transaction=transaction).delete()
            else:
                Transaction.objects.filter(related_transaction=transaction.related_transaction).delete()
                transaction.related_transaction.delete()

        transaction.delete()
        return Response({'worked': True})

    @action(detail=False, methods=['patch'])
    def pay(self, request):
        transaction_id = request.data.get('transaction_id')
        if not transaction_id:
            return Response({"error": "Transaction ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            transaction = Transaction.objects.get(id=transaction_id, created_by=request.user)
            transaction.is_paid = True
            transaction.date_payment = datetime.datetime.today()

            receipt_image_base64 = request.data.get('receipt_image')
            if receipt_image_base64:
                format, imgstr = receipt_image_base64.split(';base64,')
                ext = format.split('/')[-1]
                image = ContentFile(base64.b64decode(imgstr), name=f'receipt_{transaction_id}.{ext}')
                transaction.receipt = image

            transaction.save()
            return Response({"message": "Transaction marked as paid."})
        except Transaction.DoesNotExist:
            return Response({"error": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['patch'])
    def cancel_payment(self, request):
        transaction_id = request.data.get('transaction_id')
        if not transaction_id:
            return Response({"error": "Transaction ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            transaction = Transaction.objects.get(id=transaction_id, created_by=request.user)
            transaction.is_paid = False
            transaction.save()
            return Response({"message": "Transaction payment canceled successfully."})
        except Transaction.DoesNotExist:
            return Response({"error": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)
