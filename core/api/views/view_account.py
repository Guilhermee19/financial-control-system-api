from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from core.models import  Account, Transaction
from core.serializers import *

from rest_framework.permissions import IsAuthenticated


#?  -----------------------
#?  -------- Account ---------
#?  -----------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Adicione esta linha para garantir que o usuário esteja autenticado
def get_all_accounts(request):
    if request.method == 'GET':
        # Filtrar as contas criadas pelo usuário autenticado
        accounts = Account.objects.filter(created_by=request.user)

        for account in accounts:
            # Obtém todas as transações relacionadas a essa conta
            transactions = Transaction.objects.filter(account=account, created_by=request.user)

            # Calcula o saldo total com base no tipo de cada transação
            total_balance = sum(
                transaction.value_installment if transaction.type == 'INCOME' else -transaction.value_installment
                for transaction in transactions
            )

            # Atualiza o saldo da conta com o valor total calculado
            account.balance = total_balance if total_balance > 0 else 0
            account.save()  # Salva as mudanças no saldo da conta

        all_param = request.GET.get('all')

        if all_param:         
            serializer = AccountSerializer(accounts, many=True)
            return Response(serializer.data)
        else:
            # PAGINATION
            paginator = PageNumberPagination()
            paginator.page_size = request.query_params.get('page_size', 10)
            paginator.page_query_param = 'page'

            serializer = AccountSerializer(paginator.paginate_queryset(accounts, request), many=True).data
            return paginator.get_paginated_response(serializer)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_account_by_id(request):
   
    if "id" not in request.GET:
        return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    print(request.GET["id"])
    
    try: 
       account = Account.objects.get(id=request.GET["id"])
    except:
        return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = AccountSerializer(account)
    return Response(serializer.data, status=status.HTTP_200_OK)
        
        
@api_view(['POST'])
def post_account(request):
    if(request.method == 'POST'):
        user = request.user
        
        new_account = request.data.copy()
        
        # Atribua o usuário autenticado aos campos 'created_by' e 'updated_by'
        new_account['created_by'] = user.id
        new_account['updated_by'] = user.id
        new_account['balance'] = 0

        serializer = AccountSerializer(data=new_account)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
       
        # Se os dados não forem válidos, retorne os detalhes dos erros
        return Response({
            "errors": serializer.errors, 
            "message": "Erro ao validar os dados de entrada."
        }, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['PATCH'])
def update_account(request):
    if(request.method == 'PATCH'):
        if not 'id'in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            account = Account.objects.get(id=int(request.data['id']))
            account_serializer = AccountSerializer(account, data=request.data, partial=True)

            if account_serializer.is_valid():
                account_serializer.save()
            else:
                return Response(account_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(account_serializer.data)


@api_view(['DELETE'])
def delete_account(request, id):
    try:
        account = Account.objects.get(id=int(id))
        account.delete()
    except:
        return Response({'detail': 'Account not found'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'worked': True})
