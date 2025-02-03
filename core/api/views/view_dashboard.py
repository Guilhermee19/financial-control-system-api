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
        # Se não forem passadas, usar o mês atual como padrão
        today = timezone.now().date()
        start_date = today.replace(day=1)
        end_date = today

    today = timezone.now().date()

    print(f"Fetching data from {start_date} to {end_date} for user {request.user}")

    # Totais de entrada e saída do dia
    total_day_income = Transaction.objects.filter(
        expiry_date=today, type='INCOME', created_by=request.user
    ).aggregate(total=Sum('value_installment'))['total'] or 0

    total_day_expenditure = Transaction.objects.filter(
        expiry_date=today, type='EXPENDITURE', created_by=request.user
    ).aggregate(total=Sum('value_installment'))['total'] or 0

    # Totais de entrada e saída do mês
    total_month_income = Transaction.objects.filter(
        expiry_date__gte=start_date, expiry_date__lte=end_date, type='INCOME', created_by=request.user
    ).aggregate(total=Sum('value_installment'))['total'] or 0

    total_month_expenditure = Transaction.objects.filter(
        expiry_date__gte=start_date, expiry_date__lte=end_date, type='EXPENDITURE', created_by=request.user
    ).aggregate(total=Sum('value_installment'))['total'] or 0

    # Consultar as transações com base nas datas e tipos específicos
    expenditure_transactions = Transaction.objects.filter(
        expiry_date__gte=start_date,
        expiry_date__lte=end_date,
        type='EXPENDITURE',
        created_by=request.user
    ).order_by('expiry_date')

    income_transactions = Transaction.objects.filter(
        expiry_date__gte=start_date,
        expiry_date__lte=end_date,
        type='INCOME',
        created_by=request.user
    ).order_by('expiry_date')

    print(f"Found {expenditure_transactions.count()} expenditure transactions for the user.")
    print(f"Found {income_transactions.count()} income transactions for the user.")

    # Agrupar transações e calcular os totais
    transaction_summary_expenditure = []
    transaction_summary_income = []
    total_expenditure_value = 0
    total_income_value = 0

    # Gerar lista de todos os dias entre as datas
    current_date = start_date
    while current_date <= end_date:
        # Verifica se há uma transação de despesa para o dia atual
        day_expenditure_transactions = expenditure_transactions.filter(expiry_date=current_date)
        if day_expenditure_transactions.exists():
            # Se houver transações, usa o valor da última transação
            for transaction in day_expenditure_transactions:
                total_expenditure_value += transaction.value_installment
                transaction_summary_expenditure.append({
                    'day': current_date.day,
                    'value': transaction.value_installment,
                    'value_total': total_expenditure_value,
                    'type': transaction.type
                })
        else:
            # Se não houver transações, adiciona um dia com value 0
            transaction_summary_expenditure.append({
                'day': current_date.day,
                'value': 0,
                'value_total': total_expenditure_value,
                'type': 'EXPENDITURE'  # Ou outro tipo padrão se necessário
            })

        # Verifica se há uma transação de receita para o dia atual
        day_income_transactions = income_transactions.filter(expiry_date=current_date)
        if day_income_transactions.exists():
            # Se houver transações, usa o valor da última transação
            for transaction in day_income_transactions:
                total_income_value += transaction.value
                transaction_summary_income.append({
                    'day': current_date.day,
                    'value': transaction.value,
                    'value_total': total_income_value,
                    'type': transaction.type
                })
        else:
            # Se não houver transações, adiciona um dia com value 0
            transaction_summary_income.append({
                'day': current_date.day,
                'value': 0,
                'value_total': total_income_value,
                'type': 'INCOME'  # Ou outro tipo padrão se necessário
            })

        current_date += timedelta(days=1)

    # Retornar todos os dados em um único Response
    return Response({
        'total_day_income': total_day_income,
        'total_day_expenditure': total_day_expenditure,
        'total_month_income': total_month_income,
        'total_month_expenditure': total_month_expenditure,
        'transaction_summary_expenditure': transaction_summary_expenditure,
        'transaction_summary_income': transaction_summary_income,
    })
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_new(request):
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
        'balance': balance if balance > 0 else 0,
        'total_income': total_income,
        'total_expenditure': total_expenditure,
        'category_percentages': category_percentages
    })