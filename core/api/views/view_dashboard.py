from django.db.models import Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import  IsAuthenticated
from core.models import Transaction
from core.serializers import *
import datetime  # Importar o módulo completo para evitar conflito
from django.utils.timezone import make_aware
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

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
    # Obter a data de início e fim da query
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Converter strings de data para objetos datetime.date
    if start_date and end_date:
        try:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Formato de data inválido, use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        today = timezone.now().date()
        start_date = today.replace(day=1)  # Primeiro dia do mês atual
        end_date = today  # Hoje

    # Obter todas as categorias existentes
    all_categories = Category.objects.filter(created_by=request.user).values_list('name', flat=True)

    # Totais de entrada e saída do mês
    total_expenditure = Transaction.objects.filter(
        expiry_date__range=(start_date, end_date), type='EXPENDITURE', created_by=request.user
    ).aggregate(total=Sum('value_installment'))['total'] or 0

    # Inicializar todas as categorias com 0
    category_data = {category: {"name": category, "percentage": 0, "total_spent": 0} for category in all_categories}

    # Calcular percentuais de cada categoria e o valor gasto em cada uma
    category_expenditures = Transaction.objects.filter(
        expiry_date__range=(start_date, end_date),
        type='EXPENDITURE',
        created_by=request.user
    ).values('category__name').annotate(
        total_category_expenditure=Sum('value_installment')
    )

    # Atualizar os valores das categorias que possuem transações
    for category in category_expenditures:
        category_name = category['category__name'] or "Outros"
        total_spent = category['total_category_expenditure']
        percent = (total_spent / total_expenditure * 100) if total_expenditure else 0

        category_data[category_name] = {
            "name": category_name,
            "percentage": round(percent, 2),
            "total_spent": total_spent
        }

    # Retornar os dados em formato de lista
    return Response(list(category_data.values()))

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
    return Response({
        'category_percentages': category_percentages
    })
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_upcoming_and_unpaid_transactions(request):
    if request.method == 'GET':
        # Obter a data de início e fim a partir dos parâmetros da query
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Converter strings de data para objetos datetime.date ou definir padrão
        if start_date and end_date:
            try:
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({"error": "Formato de data inválido, use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            today = timezone.now().date()
            start_date = today.replace(day=1)  # Primeiro dia do mês atual
            end_date = today  # Hoje

        # Pegar a data de hoje para separar vencidos e futuros corretamente
        today = timezone.now().date()

        # Transações futuras (próximos 10 vencimentos)
        upcoming_transactions = Transaction.objects.filter(
            expiry_date__gte=today,  # Apenas futuras (hoje ou depois)
            expiry_date__range=(start_date, end_date),
            created_by=request.user
        ).order_by('expiry_date')[:10]

        # Transações vencidas e não pagas
        overdue_unpaid_transactions = Transaction.objects.filter(
            expiry_date__lt=today,  # Apenas vencidas
            expiry_date__range=(start_date, end_date),
            is_paid=False,
            created_by=request.user
        ).order_by('expiry_date')

        # Serializar os dados
        upcoming_serializer = TransactionSerializer(upcoming_transactions, many=True)
        overdue_serializer = TransactionSerializer(overdue_unpaid_transactions, many=True)

        return Response({
            "upcoming": upcoming_serializer.data,
            "overdue_unpaid": overdue_serializer.data
        })
    
    return Response(status=status.HTTP_400_BAD_REQUEST)