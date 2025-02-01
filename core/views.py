import base64
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.db.models import Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from .models import User, Category, Account, Transaction
from .serializers import *
import datetime  # Importar o módulo completo para evitar conflito
from datetime import timedelta
from dateutil.relativedelta import relativedelta  # Para adicionar meses e anos

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import json
import httplib2
import certifi

@api_view(['POST'])
@permission_classes([AllowAny])
def auth_user(request):

    if not 'email' in request.data:
        return Response({'detail': 'Falta o parâmetro email'}, status=status.HTTP_400_BAD_REQUEST)

    if not 'password' in request.data:
        return Response({'detail': 'Falta o parâmetro password'}, status=status.HTTP_400_BAD_REQUEST)

    print(request.data)
    
    try:
        user = User.objects.get(
            email__iexact=request.data["email"], is_deleted=False)
        
    except Exception as e:
        return Response({"detail": "E-mail ou senha incorretos! 1"}, status=status.HTTP_400_BAD_REQUEST)

    if user.is_active == True:

        if user.is_deleted == True:
            return Response({"detail": "Usuário deletado!"}, status=status.HTTP_400_BAD_REQUEST)

        print(user)
        print(user.check_password(request.data["password"]))
        
        if user.check_password(request.data["password"]):

            try:
                token, created = Token.objects.get_or_create(user=user)

                # update_last_login(None, user)

                return Response(
                    {
                        "token": token.key,
                    }
                )

            except Exception as e:
                return Response({"detail": "E-mail ou senha incorretos! 2"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"detail": "E-mail ou senha incorretos! 3"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"detail": "E-mail ou senha incorretos! 4"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user)  # Filtrando as notificações do usuário
    serializer = NotificationSerializer(notifications, many=True)  # Passando o QuerySet com many=True
    return Response(serializer.data)  # Retornando os dados serializados

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()  # Certifique-se de que isso esteja definido
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtra as notificações do usuário autenticado
        return Notification.objects.filter(user=self.request.user).order_by('-timestamp')

    def list(self, request, *args, **kwargs):
        # Método para obter notificações
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # Método para criar notificações
        notification = serializer.save()
        channel_layer = get_channel_layer()
        # Envie a notificação pelo WebSocket
        async_to_sync(channel_layer.group_send)(
            f'user_{notification.user.id}',
            {
                'type': 'send_notification',
                'message': notification.message
            }
        )
        
        
@api_view(['POST'])
# @permission_classes([AllowAny])
def social_network(request):

    social = request.data['social_network']
    if social == 'Facebook':
        url = "https://graph.facebook.com/me/?access_token=%s&fields=email" % request.data['token']
    else:
        url = "https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=%s" % request.data['token']

    http = httplib2.Http(ca_certs=certifi.where())
    response = http.request(uri=url, method='GET')

    print(response)
    
    try:
        obj = json.loads(response[1])
        print(obj)
        
        email = obj['email']

    except Exception as e:
        return Response({"error": "Não foi possível logar com as credenciais informadas."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)

    except:

        if social == "Google" or social == "google" and "access_token" in request.data:

            #Carregando informações da API:

            url = "https://people.googleapis.com/v1/people/me?personFields=birthdays,names&access_token=%s" % request.data['access_token']

            http = httplib2.Http(ca_certs=certifi.where())
            response = http.request(uri=url, method='GET')

            obj = json.loads(response[1])

            user = User.objects.create(
                email = email,
                is_admin=False
                # is_active=False
            )

            if "names" in obj and len(obj["names"]) > 0:

                name = obj["names"][0]["displayName"]

                user.name = name

            user.save()

        else:
            return Response({"error": "Não foi possível logar com as credenciais informadas!"}, status=status.HTTP_400_BAD_REQUEST)


    token, created = Token.objects.get_or_create(user=user)
    response = {'token': token.key}
    return Response(response, status=status.HTTP_200_OK)


#?  ----------------------
#?  ------- USERS --------
#?  ----------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):

    user = request.user

    user_serializer = UserSerializer(user).data

    return Response(user_serializer)


@api_view(['GET'])
def get_all_users(request):
    if(request.method == 'GET'):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_user_by_id(request):
   
    if "id" not in request.GET:
        return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    print(request.GET["id"])
    
    try: 
       user = User.objects.get(id=request.GET["id"])
    except:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)
        
        
@api_view(['POST'])
@permission_classes([AllowAny])
def post_user(request):
    if request.method == 'POST':
        new_user = request.data
        serializer = UserSerializer(data=new_user)


        if serializer.is_valid():
            item = serializer.save()
            item.set_password(request.data["password"])
            item.save()

            # Remove o .data aqui
            serializer = UserSerializer(item)
        
            return Response(serializer.data, status=status.HTTP_201_CREATED)
       
        # Se os dados do Transaction não forem válidos, retorne os detalhes dos erros
        return Response({
            "errors": serializer.errors,
            "message": "Erro ao validar os dados do Transaction."
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = request.user  # Pega o usuário autenticado a partir do token
    
    # Atualize o usuário com os dados recebidos
    serializer = UserSerializer(user, data=request.data, partial=True)  # `partial=True` permite atualizar apenas campos específicos

    if serializer.is_valid():
        item = serializer.save()

        # Se a senha for fornecida, a senha precisa ser tratada separadamente
        if "password" in request.data:
            item.set_password(request.data["password"])
            item.save()

        return Response(UserSerializer(item).data, status=status.HTTP_200_OK)
    
    return Response({
        "errors": serializer.errors,
        "message": "Erro ao validar os dados do usuário."
    }, status=status.HTTP_400_BAD_REQUEST)


#?  ----------------------
#?  ------- PLANS --------
#?  ----------------------
@api_view(['GET'])
def get_all_plan(request):

    plans = Plan.objects.filter(is_active=True)
    serializer = PlanSerializer(plans, many=True)
    return Response(serializer.data)



#?  -----------------------
#?  -------- CATERIES ---------
#?  -----------------------
@api_view(['GET'])
def get_all_categories(request):
    if(request.method == 'GET'):
        categories = Category.objects.filter(created_by = request.user)
    
        # PAGINATION
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 10)
        paginator.page_query_param = 'page'
        
        serializer = CategorySerializer(paginator.paginate_queryset(categories, request), many=True).data
        return paginator.get_paginated_response(serializer)

    
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_category_by_id(request):
   
    if "id" not in request.GET:
        return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    print(request.GET["id"])
    
    try: 
       category = Category.objects.get(id=request.GET["id"])
    except:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CategorySerializer(category)
    return Response(serializer.data, status=status.HTTP_200_OK)
        
        
@api_view(['POST'])
def post_category(request):
    if(request.method == 'POST'):
        
        # Obtenha o usuário autenticado
        user = request.user
        
        new_category = request.data
        
        # Atribua o usuário autenticado aos campos 'created_by' e 'updated_by' do Transaction
        new_category['created_by'] = user.id
        new_category['updated_by'] = user.id

        # Serializar os dados recebidos para Transaction
        serializer = CategorySerializer(data=new_category)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
       
        # Se os dados do Transaction não forem válidos, retorne os detalhes dos erros
        return Response({
            "errors": serializer.errors,
            "message": "Erro ao validar os dados do Transaction."
        }, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PATCH'])
def update_category(request, id):  # Recebe o id diretamente da URL
    try:
        # Busca a category pelo ID capturado da URL
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    # Faz a atualização parcial da category
    category_serializer = CategorySerializer(category, data=request.data, partial=True)

    if category_serializer.is_valid():
        category_serializer.save()
        return Response(category_serializer.data)
    else:
        return Response(category_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['DELETE'])
def delete_category(request, id):
    try:
        category = Category.objects.get(id=int(id))
        category.delete()
    except:
        return Response({'detail': 'Category not found'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'worked': True})


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

#?  -----------------------
#?  -------- Cards ---------
#?  -----------------------
@api_view(['GET'])
def get_all_cards(request):
    if(request.method == 'GET'):

        cards = Card.objects.filter(
            created_by  = request.user
        )
        
        # PAGINATION
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 10)
        paginator.page_query_param = 'page'

        serializer = CardSerializer(paginator.paginate_queryset(cards, request), many=True).data
        return paginator.get_paginated_response(serializer)
    
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def post_card(request):
    if(request.method == 'POST'):
        user = request.user
        
        new_card = request.data.copy()
        
        # Atribua o usuário autenticado aos campos 'created_by' e 'updated_by'
        new_card['created_by'] = user.id
        new_card['updated_by'] = user.id
        new_card['is_active'] = True

        serializer = CardSerializer(data=new_card)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
       
        # Se os dados não forem válidos, retorne os detalhes dos erros
        return Response({
            "errors": serializer.errors, 
            "message": "Erro ao validar os dados de entrada."
        }, status=status.HTTP_400_BAD_REQUEST)
        
        
#?  -----------------------
#?  -------- Transaction ---------
#?  -----------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_transaction(request):
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Ensure start_date and end_date are provided and valid
        if not start_date or not end_date:
            return Response({"error": "start_date and end_date are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return Response({"error": "Invalid date format, use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

        # transactions = Transaction.objects.all()
        
        transactions = Transaction.objects.filter(
            expiry_date__gte=start_date,
            expiry_date__lte=end_date,
            created_by=request.user
        ).order_by('expiry_date')
        
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_transaction_by_id(request):
   
    if "id" not in request.GET:
        return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try: 
       transaction = Transaction.objects.get(id=request.GET["id"])
    except:
        return Response({"error": "transaction not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = TransactionSerializer(transaction)
    return Response(serializer.data, status=status.HTTP_200_OK)
        
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_transaction(request):
    if request.method == 'POST':
        user = request.user
        
        # Obter os dados da requisição
        data = request.data.copy()
        installments = int(data.get('installments', 1))  # Garantir que é um inteiro
        
        # Atribuir o ID do usuário autenticado aos campos 'created_by' e 'updated_by'
        data['created_by'] = user.id  # Atribui o ID do usuário
        data['updated_by'] = user.id  # Atribui o ID do usuário
        
        # Calcular o valor de cada parcela
        if installments > 0:
            value_installment = data.get('value', 0) / installments  # Divide o valor total pelo número de parcelas
            data['value_installment'] = value_installment  # Ajusta o valor total da transação para o valor da parcela

        # Criar a transação principal
        serializer = TransactionSerializer(data=data)
        if serializer.is_valid():
            # Salva a transação única inicial
            transaction = serializer.save(installments=installments, related_transaction=None)  
            base_expiry_date = transaction.expiry_date  # Salvar a data de vencimento base
            transaction_group = transaction.pk  # Usa o ID da transação principal como grupo

            # Se houver parcelas, criar as transações adicionais
            for i in range(1, installments):
                # Calcular a nova data de vencimento com base na recorrência
                if transaction.recurrence == 'INSTALLMENTS':
                    new_expiry_date = base_expiry_date + relativedelta(months=i)
                elif transaction.recurrence == 'WEEKLY':
                    new_expiry_date = base_expiry_date + timedelta(weeks=i)
                elif transaction.recurrence == 'MONTHLY':
                    new_expiry_date = base_expiry_date + relativedelta(months=i)
                elif transaction.recurrence == 'ANNUAL':
                    new_expiry_date = base_expiry_date + relativedelta(years=i)
                else:
                    new_expiry_date = base_expiry_date  # Para SINGLE ou outros tipos, usar a mesma data

                # Criar a nova transação com a nova data de vencimento
                Transaction.objects.create(
                    value=transaction.value,  # O valor da parcela
                    value_installment=value_installment,  # O valor da parcela
                    description=transaction.description,
                    account=transaction.account,
                    category=transaction.category,
                    expiry_date=new_expiry_date,
                    is_paid=False,  # Inicialmente não paga
                    date_payment=None,
                    receipt=None,
                    current_installment=i+1,
                    installments=installments,  # Cada transação de parcela é única
                    related_transaction=transaction,  # Associa a transação original
                    type=transaction.type,  # Copia o tipo de transação
                    recurrence=transaction.recurrence,  # Copia a recorrência da transação
                    created_by=user,  # Atribuindo a instância do usuário
                    updated_by=user   # Atribuindo a instância do usuário
                )

            return Response({"transaction_group": str(transaction_group)}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_transaction(request, transaction_id):
    if request.method == 'PATCH':
        try:
            # Buscar a transação principal
            transaction = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            return Response({"error": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)

        # Obter os dados da requisição
        data = request.data.copy()
        
        installments = int(data.get('installments', 1))  # Garantir que é um inteiro
        
          
        # Calcular o valor de cada parcela
        if installments > 0:
            value_installment = data.get('value', 0) / installments  # Divide o valor total pelo número de parcelas
            data['value_installment'] = value_installment  # Ajusta o valor total da transação para o valor da parcela
            
        # Atualizar a transação principal
        serializer = TransactionSerializer(transaction, data=data, partial=True)  # Use partial=True para permitir atualizações parciais
        if serializer.is_valid():
            updated_transaction = serializer.save()  # Salva a transação atualizada
            
            # Checar se o parâmetro edit_all_installments está definido como True
            edit_all_installments = data.get('edit_all_installments', False)

            # Se edit_all_installments for verdadeiro, atualizar todas as transações relacionadas
            if edit_all_installments:
                related_transactions = Transaction.objects.filter(related_transaction=updated_transaction)

                # Calcular o novo valor da parcela, se houver parcelas
                total_value = updated_transaction.value
                installments = updated_transaction.installments

                if installments > 0:
                    new_value_installment = total_value / installments
                    
                    # Atualizar o value_installment e o related_transaction das transações relacionadas
                    related_transactions.update(
                        value_installment=new_value_installment, 
                        value=data['value'], 
                        description=data['description'], 
                        account=data['account'], 
                        category=data['category'], 
                        related_transaction=updated_transaction
                    )

            return Response({"message": "Transaction updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_transaction(request, id):
    try:
        transaction = Transaction.objects.get(id=int(id))
        
        # Verifica se deve excluir todas as transações relacionadas
        all_transaction = request.query_params.get('all_transaction', 'false').lower() == 'true'
        
        if all_transaction:
            # Busca todas as transações do mesmo grupo e deleta
            Transaction.objects.filter(related_transaction=transaction).delete()
            transaction.delete()
        else:
            transaction.delete()

    except Transaction.DoesNotExist:
        return Response({'detail': 'Transaction not found'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'worked': True})

      
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def pay_transaction(request):
    transaction_id = request.data.get('transaction_id')
    receipt_image_base64 = request.data.get('receipt_image', None)

    if not transaction_id:
        return Response({"error": "Transaction ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Localizar a transação pelo ID e marcar como paga
        transaction = Transaction.objects.get(id=transaction_id, created_by=request.user)
        transaction.is_paid = True

        # Verificar se uma imagem foi enviada
        if receipt_image_base64:
            # Decodificar a imagem base64 e salvar no campo 'receipt'
            format, imgstr = receipt_image_base64.split(';base64,')
            ext = format.split('/')[-1]
            receipt_image = ContentFile(base64.b64decode(imgstr), name=f'receipt_{transaction_id}.{ext}')
            transaction.receipt = receipt_image

        transaction.save()
        return Response({"message": "Transaction marked as paid and image saved successfully."}, status=status.HTTP_200_OK)

    except Transaction.DoesNotExist:
        return Response({"error": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def cancel_pay_transaction(request):
    transaction_id = request.data.get('transaction_id')

    if not transaction_id:
        return Response({"error": "Transaction ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Localizar a transação pelo ID e marcar como não paga
        transaction = Transaction.objects.get(id=transaction_id, created_by=request.user)
        transaction.is_paid = False
        transaction.save()

        return Response({"message": "Transaction payment canceled successfully."}, status=status.HTTP_200_OK)

    except Transaction.DoesNotExist:
        return Response({"error": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def upload_transaction_image(request):
    transaction_id = request.data.get('transaction_id')
    receipt_image_base64 = request.data.get('receipt_image', None)

    if not transaction_id:
        return Response({"error": "Transaction ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    if not receipt_image_base64:
        return Response({"error": "Receipt image is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Localizar a transação pelo ID
        transaction = Transaction.objects.get(id=transaction_id, created_by=request.user)

        # Decodificar a imagem base64 e salvar no campo 'receipt'
        format, imgstr = receipt_image_base64.split(';base64,')
        ext = format.split('/')[-1]
        receipt_image = ContentFile(base64.b64decode(imgstr), name=f'receipt_{transaction_id}.{ext}')
        transaction.receipt = receipt_image
        transaction.save()

        return Response({"message": "Transaction image uploaded successfully."}, status=status.HTTP_200_OK)

    except Transaction.DoesNotExist:
        return Response({"error": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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