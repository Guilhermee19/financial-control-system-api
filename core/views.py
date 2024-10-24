import base64
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models import Prefetch
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from .models import User, Category, Account, Transaction, Installment
from .serializers import *
import datetime  # Importar o módulo completo para evitar conflito
import calendar


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
    if(request.method == 'POST'):
        
        new_user = request.data
        serializer = UserSerializer(data=new_user)


        if serializer.is_valid():
            item = serializer.save()
            item.set_password(request.data["password"])
            item.save()
        
            serializer = UserSerializer(item).data
        
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
def get_all_accounts(request):
    if(request.method == 'GET'):
        # Filtrar Transaction que possuem as Installments filtradas
        accounts = Account.objects.filter(
            created_by  = request.user
        )
        
        all  = request.GET.get('all')

        if all:         
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
        # Filtrar Transaction que possuem as Installments filtradas
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


#?  -----------------------
#?  -------- Transaction ---------
#?  -----------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_transaction(request):
    if request.method == 'GET':
        return_all = request.GET.get('return_all', 'false').lower() == 'true'
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

        # Step 1: Filter Installments within the date range
        installments = Installment.objects.filter(
            due_date__gte=start_date,
            due_date__lt=end_date
        ).order_by('due_date')

        # Step 2: Get Transaction IDs that have matching installments
        transaction_ids = installments.values_list('transaction_id', flat=True).distinct()

        # Step 3: Filter transactions that match the filtered installments and user
        transactions = Transaction.objects.filter(
            id__in=transaction_ids,
            created_by=request.user
        ).order_by('date')

        # Step 4: Attach installments to each transaction and duplicate transaction if necessary
        transaction_with_installments = []
        for transaction in transactions:
            # Get all installments for this transaction within the date range
            transaction_installments = installments.filter(transaction=transaction)

            # Loop through each installment and create a separate transaction entry for each one
            for installment in transaction_installments:
                # Serialize the transaction
                transaction_data = TransactionSerializer(transaction).data

                # Add the single installment to the transaction data
                installment_data = InstallmentSerializer(installment).data
                transaction_data['installment'] = installment_data

                # Append the transaction with this specific installment
                transaction_with_installments.append(transaction_data)

        # Step 5: If return_all is True, return all results without pagination
        if return_all:
            return Response(transaction_with_installments, status=status.HTTP_200_OK)

        # Step 6: Apply pagination
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 10)

        paginated_transactions = paginator.paginate_queryset(transaction_with_installments, request)

        return paginator.get_paginated_response(paginated_transactions)

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
def post_transaction(request):
    if request.method == 'POST':
        user = request.user
        new_transaction = request.data.copy()
        new_transaction['created_by'] = user.id
        new_transaction['updated_by'] = user.id
        
        transaction_serializer = TransactionSerializer(data=new_transaction)


        # Verifique se os dados do transaction são válidos
        if transaction_serializer.is_valid():
            transaction = transaction_serializer.save()
            recurrence = request.data.get('recurrence')
            account = float(new_transaction['account'])
            category = float(new_transaction['category'])
            value = float(new_transaction['value'])
            number_of_installments = int(request.data.get('number_of_installments', 1))
            due_date_str = new_transaction.get('date', str(datetime.datetime.now().date()))
            due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%d').date()
            
            # Cria parcelas baseadas no tipo de recorrência
            if recurrence == 'INSTALLMENTS' and number_of_installments > 0:
                create_installments(transaction, value / number_of_installments, number_of_installments, due_date, user, account, category)

            elif recurrence == 'SINGLE':
                create_installment(transaction, value, 1, due_date, user)
            
            elif recurrence == 'WEEKLY':
                create_weekly_installments(transaction, value, due_date, user)
                
            elif recurrence == 'MONTHLY':
                create_monthly_installments(transaction, value, due_date, user)
                
            elif recurrence == 'ANNUAL':
                create_annual_installments(transaction, value, due_date, user)

            return Response(transaction_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response({"errors": transaction_serializer.errors, "message": "Erro ao validar os dados do transaction."}, status=status.HTTP_400_BAD_REQUEST)
    
# Função para criar uma única parcela
def create_installment(transaction, value, current_installment, due_date, user, account, category):
    installment_data = {
        'transaction': transaction.id,
        'account': account,
        'category': category,
        'installment_value': value,
        'current_installment': current_installment,
        'due_date': due_date,
        'is_paid': False,
        'created_by': user.id,
        'updated_by': user.id
    }
    validate_and_save_installment(installment_data)

# Função para validar e salvar cada parcela
def validate_and_save_installment(installment_data):
    serializer = InstallmentSerializer(data=installment_data)
    if serializer.is_valid():
        serializer.save()
    else:
        raise ValueError(serializer.errors)

# Função para criar múltiplas parcelas
def create_installments(transaction, installment_value, number_of_installments, due_date, user, account, category):
    
    for i in range(number_of_installments):
        new_due_date = adjust_date_by_month(due_date, i)
        create_installment(transaction, installment_value, i + 1, new_due_date, user, account, category)

# Função para criar parcelas semanais até o final do ano
def create_weekly_installments(transaction, value, due_date, user, account, category):
    installment_number = 1
    while due_date <= datetime.datetime.date(due_date.year, 12, 31):
        create_installment(transaction, value, installment_number, due_date, user, account, category)
        due_date += datetime.datetime.timedelta(days=7)
        installment_number += 1

# Função para criar parcelas mensais
def create_monthly_installments(transaction, value, due_date, user, account, category):
    for i in range(13 - due_date.month):
        new_due_date = adjust_date_by_month(due_date, i)
        create_installment(transaction, value, i + 1, new_due_date, user, account, category)

# Função para criar parcelas anuais
def create_annual_installments(transaction, value, due_date, user, account, category):
    for i in range(5):
        new_due_date = adjust_date_by_year(due_date, i)
        create_installment(transaction, value, i + 1, new_due_date, user, account, category)

# Ajusta a data adicionando meses e lidando com meses curtos
def adjust_date_by_month(date, month_increment):
    new_month = (date.month + month_increment - 1) % 12 + 1
    new_year = date.year + (date.month + month_increment - 1) // 12
    last_day_of_month = calendar.monthrange(new_year, new_month)[1]
    return datetime.date(new_year, new_month, min(date.day, last_day_of_month))

# Ajusta a data adicionando anos
def adjust_date_by_year(date, year_increment):
    new_year = date.year + year_increment
    last_day_of_month = calendar.monthrange(new_year, date.month)[1]
    return datetime.date(new_year, date.month, min(date.day, last_day_of_month))
    


@api_view(['PATCH'])  # Altere de PUT para PATCH
@permission_classes([IsAuthenticated])
def update_transaction(request, transaction_id):
    print(request.data)
    
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        
        # Atualiza as informações do transaction conforme necessário
        transaction.description = request.data.get('description', transaction.description)
        transaction.value = request.data.get('value', transaction.value)
        transaction.number_of_installments = request.data.get('number_of_installments', transaction.number_of_installments)
        
        # Atualiza a account se um novo ID for fornecido
        account_id = request.data.get('account', None)
        if account_id is not None:
            try:
                transaction.account = Account.objects.get(id=account_id)  # Verifica se a account existe
            except Account.DoesNotExist:
                return Response({'error': 'Account not found'}, status=404)

        # Atualiza a categoria se um novo ID for fornecido
        category_id = request.data.get('category', None)
        if category_id is not None:
            try:
                transaction.category = Category.objects.get(id=category_id)  # Verifica se a categoria existe
            except Category.DoesNotExist:
                return Response({'error': 'Category not found'}, status=404)
            
        # Salva as mudanças no transaction
        transaction.save()

        # Verifica se a atualização é para todos os installments
        if request.data.get('edit_all_installments', False):
            new_date_str = request.data.get('date', transaction.date)
            new_date = datetime.datetime.strptime(new_date_str, '%Y-%m-%d').date()  # Converte a string para um objeto de data
            new_day = new_date.day  # Obtém o novo dia

            for installment in transaction.installments.all():
                # Mantém o mês e o ano do installment atual
                current_date = installment.date
                new_date = current_date.replace(day=new_day)  # Atualiza apenas o dia
                
                # Atualiza a data do installment
                installment.date = new_date
                installment.installment_value = request.data.get('value', installment.installment_value)
                installment.save()
        else:
            installment = Installment.objects.get(id=int(request.data['installment_id']))
            
            # Atualiza o valor do installment somente se um valor específico foi fornecido
            installment.installment_value = request.data.get('installment_value', installment.installment_value)
            installment.save()
        
        return Response({'message': 'Transaction and installments updated successfully'}, status=200)

    except Transaction.DoesNotExist:
        return Response({'error': 'Transaction not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['DELETE'])
def delete_transaction(request, id):
    try:
        transaction = Transaction.objects.get(id=int(id))
        transaction.delete()
    except:
        return Response({'detail': 'transaction not found'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'worked': True})


#?  -----------------------
#?  -------- Installment ---------
#?  -----------------------
@api_view(['GET'])
def get_Installment(request):
    if(request.method == 'GET'):
        Installments = Installment.objects.all()
        serializer = InstallmentSerializer(Installments, many=True)
        return Response(serializer.data)
    
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def get_installment(request):
    if(request.method == 'PATCH'):
        if not 'id'in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            transaction = Transaction.objects.get(id=int(request.data['id']))
            transaction_serializer = TransactionSerializer(transaction, data=request.data, partial=True)

            if transaction_serializer.is_valid():
                transaction_serializer.save()
            else:
                return Response(transaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(transaction_serializer.data)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_installment(request):
    if(request.method == 'POST'):
        
        user = request.user
        new_instalment = request.data.copy()  # Crie uma cópia dos dados do request
        
        # Atribua o usuário autenticado aos campos 'created_by' e 'updated_by'
        new_instalment['created_by'] = user.id
        new_instalment['updated_by'] = user.id
        
        # Serializar os dados recebidos
        serializer = InstallmentSerializer(data=new_instalment)

        # Verifique se os dados são válidos
        if serializer.is_valid():
            serializer.save()  # Salve o novo objeto no banco de dados
            return Response(serializer.data, status=status.HTTP_201_CREATED)
       
        # Se os dados não forem válidos, retorne os detalhes dos erros
        return Response({
            "errors": serializer.errors, 
            "message": "Erro ao validar os dados de entrada."
        }, status=status.HTTP_400_BAD_REQUEST)
        
        
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def pay_installment(request):
    if request.method == 'PATCH':
        installment_id = request.data.get('installment_id')
        installment_image_base64 = request.data.get('installment_image', None)

        if not installment_id:
            return Response({"error": "Installment ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Localizar a parcela pelo ID
            installment = Installment.objects.get(id=int(installment_id))
            
            # Atualizar o campo is_paid
            installment.is_paid = True

            # Verificar se uma imagem foi enviada
            if installment_image_base64:
                # Decodificar a imagem base64 e salvar no campo 'receipt_image'
                format, imgstr = installment_image_base64.split(';base64,')
                ext = format.split('/')[-1]
                installment_image = ContentFile(base64.b64decode(imgstr), name=f'receipt_{installment_id}.{ext}')
                installment.installment_image = installment_image
            
            installment.save()

            return Response({"message": "Installment marked as paid and image saved successfully."}, status=status.HTTP_200_OK)

        except Installment.DoesNotExist:
            return Response({"error": "Installment not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def cancell_pay_installment(request):
    if request.method == 'PATCH':
        installment_id = request.data.get('installment_id')

        if not installment_id:
            return Response({"error": "Installment ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Localizar a parcela pelo ID
            installment = Installment.objects.get(id=int(installment_id))
            
            # Atualizar o campo is_paid
            installment.is_paid = False

            installment.save()

            return Response({"message": "Installment marked as paid and image saved successfully."}, status=status.HTTP_200_OK)

        except Installment.DoesNotExist:
            return Response({"error": "Installment not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def upload_installment_image(request):
    if request.method == 'PATCH':
        installment_id = request.data.get('installment_id')
        installment_image_base64 = request.data.get('installment_image', None)

        if not installment_id:
            return Response({"error": "Installment ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not installment_image_base64:
            return Response({"error": "Installment image is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Localizar a parcela pelo ID
            installment = Installment.objects.get(id=int(installment_id))

            # Decodificar a imagem base64 e salvar no campo 'receipt_image'
            format, imgstr = installment_image_base64.split(';base64,')
            ext = format.split('/')[-1]
            installment_image = ContentFile(base64.b64decode(imgstr), name=f'receipt_{installment_id}.{ext}')
            installment.installment_image = installment_image
            installment.save()

            return Response({"message": "Installment image uploaded successfully."}, status=status.HTTP_200_OK)

        except Installment.DoesNotExist:
            return Response({"error": "Installment not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard(request):
    if request.method == 'GET':
        # Pegar as datas de início e fim passadas via request
        start_date  = request.GET.get('start_date')
        end_date    = request.GET.get('end_date')

        # Converter strings de data para objetos datetime.date
        if start_date and end_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            # Se não forem passadas, usar o mês atual como padrão
            today = timezone.now().date()
            start_date = today.replace(day=1)  # Primeiro dia do mês
            end_date = (today.replace(month=today.month % 12 + 1, day=1) - timezone.timedelta(days=1))  # Último dia do mês

        # Data de hoje sem informações de fuso horário
        today = timezone.now().date()

        # Totais de entrada e saída do dia (somente o dia atual)
        total_day_income = Installment.objects.filter(due_date=today, transaction__type='INCOME', created_by=request.user).aggregate(total=Sum('installment_value'))['total'] or 0
        total_day_expenditure = Installment.objects.filter(due_date=today, transaction__type='EXPENDITURE', created_by=request.user).aggregate(total=Sum('installment_value'))['total'] or 0

        # Totais de entrada e saída do mês (usar data >= início e <= fim)
        total_month_income = Installment.objects.filter(due_date__gte=start_date, due_date__lte=end_date, transaction__type='INCOME', created_by=request.user).aggregate(total=Sum('installment_value'))['total'] or 0
        total_month_expenditure = Installment.objects.filter(due_date__gte=start_date, due_date__lte=end_date, transaction__type='EXPENDITURE', created_by=request.user).aggregate(total=Sum('installment_value'))['total'] or 0

        # Retornar os totais como JSON
        return JsonResponse({
            'total_day_income': total_day_income,
            'total_day_expenditure': total_day_expenditure,
            'total_month_income': total_month_income,
            'total_month_expenditure': total_month_expenditure,
        })