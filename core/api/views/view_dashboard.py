from django.db.models import Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import  IsAuthenticated
from core.models import Transaction
from core.serializers import *
import datetime  # Importar o módulo completo para evitar conflito
from datetime import timedelta

from rest_framework.permissions import IsAuthenticated


#?  -----------------------
#?  -------- Dashboard ---------
#?  -----------------------  


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard(request):
    # Obter a data de início e fim a partir dos parâmetros da query
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Converter strings de data para objetos datetime.date
    if start_date and end_date:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        today = timezone.now().date()
        start_date = today.replace(day=1)
        end_date = today

    # Totais de entrada e saída do mês
    total_income = Transaction.objects.filter(
        expiry_date__gte=start_date, expiry_date__lte=end_date, type='INCOME', created_by=request.user
    ).aggregate(total=Sum('value_installment'))['total'] or 0

    total_expenditure = Transaction.objects.filter(
        expiry_date__gte=start_date, expiry_date__lte=end_date, type='EXPENDITURE', created_by=request.user
    ).aggregate(total=Sum('value_installment'))['total'] or 0

    balance = total_income - total_expenditure

    # Retornar todos os dados em um único Response
    return Response({
        'balance': balance if balance > 0 else 0,
        'total_income': total_income,
        'total_expenditure': total_expenditure,
    })
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_category(request):
    # Obter a data de início e fim a partir dos parâmetros da query
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Converter strings de data para objetos datetime.date
    if start_date and end_date:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        today = timezone.now().date()
        start_date = today.replace(day=1)
        end_date = today

    # Totais de entrada e saída do mês
    total_expenditure = Transaction.objects.filter(
        expiry_date__gte=start_date, expiry_date__lte=end_date, type='EXPENDITURE', created_by=request.user
    ).aggregate(total=Sum('value_installment'))['total'] or 0
    
    # Calcular percentuais de cada categoria e o valor gasto em cada uma
    category_expenditures = Transaction.objects.filter(
        expiry_date__gte=start_date,
        expiry_date__lte=end_date,
        type='EXPENDITURE',
        created_by=request.user
    ).values('category__name').annotate(
        total_category_expenditure=Sum('value_installment')
    )

    category_percentages = []
    for category in category_expenditures:
        total_expenditure_for_category = category['total_category_expenditure']
        percent = (total_expenditure_for_category / total_expenditure * 100) if total_expenditure else 0
        category_percentages.append({
            'name': category['category__name'] if category['category__name'] else "Outros" ,
            'percentage': round(percent, 2),
            'total_spent': total_expenditure_for_category
        })

    # Retornar todos os dados em um único Response
    return Response(category_percentages)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_expenditure_income(request):
    # Obter a data de início e fim a partir dos parâmetros da query
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Converter strings de data para objetos datetime.date
    if start_date and end_date:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        today = timezone.now().date()
        start_date = today.replace(day=1)
        end_date = today

    # Totais de entrada e saída do mês
    total_income = Transaction.objects.filter(
        expiry_date__gte=start_date, expiry_date__lte=end_date, type='INCOME', created_by=request.user
    ).aggregate(total=Sum('value_installment'))['total'] or 0

    total_expenditure = Transaction.objects.filter(
        expiry_date__gte=start_date, expiry_date__lte=end_date, type='EXPENDITURE', created_by=request.user
    ).aggregate(total=Sum('value_installment'))['total'] or 0

    # Calcular percentuais de cada categoria e o valor gasto em cada uma
    category_expenditures = Transaction.objects.filter(
        expiry_date__gte=start_date,
        expiry_date__lte=end_date,
        type='EXPENDITURE',
        created_by=request.user
    ).values('category__name').annotate(
        total_category_expenditure=Sum('value_installment')
    )

    category_percentages = []
    for category in category_expenditures:
        total_expenditure_for_category = category['total_category_expenditure']
        percent = (total_expenditure_for_category / total_expenditure * 100) if total_expenditure else 0
        category_percentages.append({
            'name': category['category__name'] if category['category__name'] else "Outros" ,
            'percentage': round(percent, 2),
            'total_spent': total_expenditure_for_category
        })

    balance = total_income - total_expenditure

    # Retornar todos os dados em um único Response
    return Response({
        'category_percentages': category_percentages
    })