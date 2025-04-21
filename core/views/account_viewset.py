from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from core.models import Account, Transaction
from core.serializers import AccountSerializer


class AccountViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        accounts = Account.objects.filter(created_by=request.user)

        # Atualiza o saldo de cada conta com base nas transações
        for account in accounts:
            transactions = Transaction.objects.filter(account=account, created_by=request.user)
            total_balance = sum(
                t.value_installment if t.type == 'INCOME' else -t.value_installment for t in transactions
            )
            account.balance = total_balance if total_balance > 0 else 0
            account.save()

        if request.GET.get("all"):
            serializer = AccountSerializer(accounts, many=True)
            return Response(serializer.data)

        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 10)
        result_page = paginator.paginate_queryset(accounts, request)
        serializer = AccountSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        data = request.data.copy()
        data['created_by'] = request.user.id
        data['updated_by'] = request.user.id
        data['balance'] = 0

        serializer = AccountSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({
            "errors": serializer.errors,
            "message": "Erro ao validar os dados da conta."
        }, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        account = get_object_or_404(Account, pk=pk)
        serializer = AccountSerializer(account, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        account = get_object_or_404(Account, pk=pk)
        account.delete()
        return Response({"worked": True})

    @action(detail=False, methods=["get"])
    def by_id(self, request):
        account_id = request.GET.get("id")
        if not account_id:
            return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = Account.objects.get(id=account_id)
            serializer = AccountSerializer(account)
            return Response(serializer.data)
        except Account.DoesNotExist:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
