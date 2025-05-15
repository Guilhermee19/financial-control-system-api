from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
import datetime

from core.models import Transaction, Category
from core.serializers import TransactionSerializer


class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def _get_dates(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date and end_date:
            try:
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError("Formato de data inválido, use YYYY-MM-DD")
        else:
            today = timezone.now().date()
            start_date = today.replace(day=1)
            end_date = today
        return start_date, end_date

    @action(detail=False, methods=['get'])
    def resumo(self, request):
        try:
            start_date, end_date = self._get_dates(request)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        total_income = Transaction.objects.filter(
            expiry_date__range=(start_date, end_date),
            type='INCOME',
            created_by=request.user
        ).aggregate(total=Sum('value_installment'))['total'] or 0

        total_income_paid = Transaction.objects.filter(
            expiry_date__range=(start_date, end_date),
            type='INCOME',
            is_paid=True,
            created_by=request.user
        ).aggregate(total=Sum('value_installment'))['total'] or 0

        total_expenditure = Transaction.objects.filter(
            expiry_date__range=(start_date, end_date),
            type='EXPENDITURE',
            created_by=request.user
        ).aggregate(total=Sum('value_installment'))['total'] or 0

        total_expenditure_paid = Transaction.objects.filter(
            expiry_date__range=(start_date, end_date),
            type='EXPENDITURE',
            is_paid=True,
            created_by=request.user
        ).aggregate(total=Sum('value_installment'))['total'] or 0

        balance = total_income_paid - total_expenditure_paid

        return Response({
            'balance': balance if balance > 0 else 0,
            'total_income': total_income,
            'total_expenditure': total_expenditure,
        })

    @action(detail=False, methods=['get'])
    def categorias(self, request):
        try:
            start_date, end_date = self._get_dates(request)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        all_categories = Category.objects.filter(created_by=request.user).values_list('name', flat=True)
        total_expenditure = Transaction.objects.filter(
            expiry_date__range=(start_date, end_date),
            type='EXPENDITURE',
            created_by=request.user
        ).aggregate(total=Sum('value_installment'))['total'] or 0

        category_data = {name: {"name": name, "percentage": 0, "total_spent": 0} for name in all_categories}

        category_expenditures = Transaction.objects.filter(
            expiry_date__range=(start_date, end_date),
            type='EXPENDITURE',
            created_by=request.user
        ).values('category__name').annotate(
            total_category_expenditure=Sum('value_installment')
        )

        for cat in category_expenditures:
            name = cat['category__name'] or "Outros"
            spent = cat['total_category_expenditure']
            percent = (spent / total_expenditure * 100) if total_expenditure else 0

            category_data[name] = {
                "name": name,
                "percentage": round(percent, 2),
                "total_spent": spent
            }

        return Response(list(category_data.values()))

    @action(detail=False, methods=['get'])
    def categoria_percentual(self, request):
        try:
            start_date, end_date = self._get_dates(request)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        total_expenditure = Transaction.objects.filter(
            expiry_date__range=(start_date, end_date),
            type='EXPENDITURE',
            created_by=request.user
        ).aggregate(total=Sum('value_installment'))['total'] or 0

        category_percentages = []
        category_expenditures = Transaction.objects.filter(
            expiry_date__range=(start_date, end_date),
            type='EXPENDITURE',
            created_by=request.user
        ).values('category__name').annotate(
            total_category_expenditure=Sum('value_installment')
        )

        for cat in category_expenditures:
            name = cat['category__name'] or "Outros"
            spent = cat['total_category_expenditure']
            percent = (spent / total_expenditure * 100) if total_expenditure else 0

            category_percentages.append({
                "name": name,
                "percentage": round(percent, 2),
                "total_spent": spent
            })

        return Response({"category_percentages": category_percentages})

    @action(detail=False, methods=['get'])
    def transacoes_futuras_vencidas(self, request):
        try:
            start_date, end_date = self._get_dates(request)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        today = timezone.now().date()

        upcoming = Transaction.objects.filter(
            expiry_date__range=(start_date, end_date),
            is_paid=False,
            created_by=request.user
        ).order_by('expiry_date')[:10]

        overdue = Transaction.objects.filter(
            expiry_date__lt=today,
            expiry_date__range=(start_date, end_date),
            is_paid=False,
            created_by=request.user
        ).order_by('expiry_date')

        return Response({
            "upcoming": TransactionSerializer(upcoming, many=True).data,
            "overdue_unpaid": TransactionSerializer(overdue, many=True).data,
        })
