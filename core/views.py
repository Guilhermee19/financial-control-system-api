from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import User, Tag, Conta, Finance, Parcela, FinanceEntry
from .serializers import *
from rest_framework.pagination import PageNumberPagination
import datetime  # Importar o módulo completo para evitar conflito
import calendar

import json
import httplib2
import certifi
import datetime

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
        else:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
       
        item.set_password(request.data["password"])
        item.save()
       
        serializer = UserSerializer(item).data
       
        # Se os dados do Finance não forem válidos, retorne os detalhes dos erros
        return Response({
            "errors": serializer.errors,
            "message": "Erro ao validar os dados do finance."
        }, status=status.HTTP_400_BAD_REQUEST)


#?  -----------------------
#?  -------- TAGS ---------
#?  -----------------------
@api_view(['GET'])
def get_all_tags(request):
    if(request.method == 'GET'):
        tags = Tag.objects.filter(created_by = request.user)
    
        # PAGINATION
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 10)
        paginator.page_query_param = 'page'
        
        serializer = TagSerializer(paginator.paginate_queryset(tags, request), many=True).data
        return paginator.get_paginated_response(serializer)

    
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_tag_by_id(request):
   
    if "id" not in request.GET:
        return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    print(request.GET["id"])
    
    try: 
       tag = Tag.objects.get(id=request.GET["id"])
    except:
        return Response({"error": "Tag not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = TagSerializer(tag)
    return Response(serializer.data, status=status.HTTP_200_OK)
        
        
@api_view(['POST'])
def post_tag(request):
    if(request.method == 'POST'):
        
        # Obtenha o usuário autenticado
        user = request.user
        
        new_tag = request.data
        
        # Atribua o usuário autenticado aos campos 'created_by' e 'updated_by' do Finance
        new_tag['created_by'] = user.id
        new_tag['updated_by'] = user.id

        # Serializar os dados recebidos para Finance
        serializer = TagSerializer(data=new_tag)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
       
        # Se os dados do Finance não forem válidos, retorne os detalhes dos erros
        return Response({
            "errors": serializer.errors,
            "message": "Erro ao validar os dados do finance."
        }, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PATCH'])
def update_tag(request):
    if(request.method == 'PATCH'):
        if not 'id'in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            tag = Tag.objects.get(id=int(request.data['id']))
            tag_serializer = TagSerializer(tag, data=request.data, partial=True)

            if tag_serializer.is_valid():
                tag_serializer.save()
            else:
                return Response(tag_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(tag_serializer.data)


@api_view(['DELETE'])
def delete_tag(request, id):
    try:
        tag = Tag.objects.get(id=int(id))
        tag.delete()
    except:
        return Response({'detail': 'Tag not found'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'worked': True})


#?  -----------------------
#?  -------- CONTA ---------
#?  -----------------------
@api_view(['GET'])
def get_all_contas(request):
    if(request.method == 'GET'):
        accounts = Conta.objects.all()
        all  = request.GET.get('all')

        if all:         
            serializer = ContaSerializer(accounts, many=True)
            return Response(serializer.data)
        else:
            # PAGINATION
            paginator = PageNumberPagination()
            paginator.page_size = request.query_params.get('page_size', 10)
            paginator.page_query_param = 'page'

            serializer = ContaSerializer(paginator.paginate_queryset(accounts, request), many=True).data
            return paginator.get_paginated_response(serializer)
    
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_conta_by_id(request):
   
    if "id" not in request.GET:
        return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    print(request.GET["id"])
    
    try: 
       conta = Conta.objects.get(id=request.GET["id"])
    except:
        return Response({"error": "Conta not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ContaSerializer(conta)
    return Response(serializer.data, status=status.HTTP_200_OK)
        
        
@api_view(['POST'])
def post_conta(request):
    if(request.method == 'POST'):
        user = request.user
        
        new_conta = request.data.copy()
        
        # Atribua o usuário autenticado aos campos 'created_by' e 'updated_by'
        new_conta['created_by'] = user.id
        new_conta['updated_by'] = user.id
        new_conta['balance_debit'] = 0
        new_conta['balance_credit'] = 0

        serializer = ContaSerializer(data=new_conta)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
       
        # Se os dados não forem válidos, retorne os detalhes dos erros
        return Response({
            "errors": serializer.errors, 
            "message": "Erro ao validar os dados de entrada."
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def update_conta(request):
    if(request.method == 'PATCH'):
        if not 'id'in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            conta = Conta.objects.get(id=int(request.data['id']))
            conta_serializer = ContaSerializer(conta, data=request.data, partial=True)

            if conta_serializer.is_valid():
                conta_serializer.save()
            else:
                return Response(conta_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(conta_serializer.data)


@api_view(['DELETE'])
def delete_conta(request, id):
    try:
        conta = Conta.objects.get(id=int(id))
        conta.delete()
    except:
        return Response({'detail': 'Conta not found'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'worked': True})


#?  -----------------------
#?  -------- FINANCE ---------
#?  -----------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_finances(request):
    if(request.method == 'GET'):
        
        start_date  = request.GET.get('start_date')
        end_date    = request.GET.get('end_date')

        # Filtrar parcelas dentro do intervalo de datas
        installments = Parcela.objects.filter(
            date__gte   = start_date,
            date__lt    = end_date
        ).values_list('finance', flat=True).distinct()
        
        # Ordenar por data
        installments_order = installments.order_by('date')

        # Filtrar finances que possuem as parcelas filtradas
        finances = Finance.objects.filter(
            id__in      = installments_order,
            created_by  = request.user
        )
        
        # PAGINATION
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 10)
        paginator.page_query_param = 'page'

        serializer = FinanceSerializer(paginator.paginate_queryset(finances, request), many=True).data
        for item in serializer:
            parcela = Parcela.objects.filter(   
                finance_id = item['id'],
                date__gte   = start_date,
                date__lt    = end_date
            ).first()
            
            item['parcela'] =  ParcelaSerializer(parcela).data
        return paginator.get_paginated_response(serializer)
    
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_finance_by_id(request):
   
    if "id" not in request.GET:
        return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    print(request.GET["id"])
    
    try: 
       finance = Finance.objects.get(id=request.GET["id"])
    except:
        return Response({"error": "Finance not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = FinanceSerializer(finance)
    return Response(serializer.data, status=status.HTTP_200_OK)
        
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_finance(request):
    if request.method == 'POST':
        
        # Obtenha o usuário autenticado
        user = request.user
        
        # Crie uma cópia dos dados recebidos no request para o Finance
        new_finance = request.data.copy()
        
        # Atribua o usuário autenticado aos campos 'created_by' e 'updated_by' do Finance
        new_finance['created_by'] = user.id
        new_finance['updated_by'] = user.id
        
 
        
        # Serializar os dados recebidos para Finance
        finance_serializer = FinanceSerializer(data=new_finance)

        # Verifique se os dados do Finance são válidos
        if finance_serializer.is_valid():
            # Salve o novo objeto Finance no banco de dados
            finance = finance_serializer.save()

            # Verifique se a variável 'number_of_installments' foi enviada e é maior que 1
            number_of_installments = int(request.data.get('number_of_installments', 1))

            if number_of_installments > 0:
                # Obtenha informações relevantes do Finance
                total_amount = float(new_finance['value'])  # Valor total do Finance
                installment_value = total_amount / number_of_installments  # Valor de cada parcela
                
                # Pegar a data separando dia, mês e ano
                due_date_str = new_finance.get('date', str(datetime.datetime.now().date()))  # Data inicial como string
                due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%d')  # Convertendo para objeto datetime
                day = due_date.day
                month = due_date.month
                year = due_date.year

                # Crie as parcelas automaticamente
                for i in range(number_of_installments):
                    # Ajuste o mês e ano para a parcela
                    new_month = (month + i) % 12 or 12  # Garantir que o mês fique entre 1 e 12
                    new_year = year + (month + i - 1) // 12  # Ajustar o ano conforme os meses aumentam

                    # Garantir que o dia seja válido para o mês (caso, por exemplo, fevereiro tenha menos dias)
                    last_day_of_new_month = calendar.monthrange(new_year, new_month)[1]
                    new_day = min(day, last_day_of_new_month)  # Ajusta o dia se for maior que o último dia do mês

                    # Montar a nova data para a parcela
                    new_due_date = datetime.datetime(new_year, new_month, new_day).date()

                    parcela_data = {
                        'finance': finance.id,
                        'installment_value': installment_value,
                        'current_installment': i + 1,
                        'date': new_due_date,  # Definindo a data da parcela
                        'is_paid': False,
                        'created_by': user.id,
                        'updated_by': user.id
                         # Atribua o usuário autenticado aos campos 'created_by' e 'updated_by'
                    }

                    # Serializar e validar cada parcela
                    parcela_serializer = ParcelaSerializer(data=parcela_data)
                    
                    if parcela_serializer.is_valid():
                        parcela_serializer.save()
                    else:
                        # Caso algum dado da parcela seja inválido, retorne os erros
                        return Response({
                            "errors": parcela_serializer.errors,
                            "message": "Erro ao validar os dados da parcela."
                        }, status=status.HTTP_400_BAD_REQUEST)

            # Retorne o finance criado com status 201 CREATED
            return Response(finance_serializer.data, status=status.HTTP_201_CREATED)

        # Se os dados do Finance não forem válidos, retorne os detalhes dos erros
        return Response({
            "errors": finance_serializer.errors,
            "message": "Erro ao validar os dados do finance."
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def update_finance(request):
    if(request.method == 'PATCH'):
        if not 'id'in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            finance = Finance.objects.get(id=int(request.data['id']))
            finance_serializer = FinanceSerializer(finance, data=request.data, partial=True)

            if finance_serializer.is_valid():
                finance_serializer.save()
            else:
                return Response(finance_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(finance_serializer.data)


@api_view(['DELETE'])
def delete_finance(request, id):
    try:
        finance = Finance.objects.get(id=int(id))
        finance.delete()
    except:
        return Response({'detail': 'Finance not found'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'worked': True})


#?  -----------------------
#?  -------- PARCELA ---------
#?  -----------------------
@api_view(['GET'])
def get_parcela(request):
    if(request.method == 'GET'):
        parcelas = Parcela.objects.all()
        serializer = ParcelaSerializer(parcelas, many=True)
        return Response(serializer.data)
    
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def pay_instalment(request):
    if(request.method == 'PATCH'):
        if not 'id'in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            finance = Finance.objects.get(id=int(request.data['id']))
            finance_serializer = FinanceSerializer(finance, data=request.data, partial=True)

            if finance_serializer.is_valid():
                finance_serializer.save()
            else:
                return Response(finance_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(finance_serializer.data)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_parcela(request):
    if(request.method == 'POST'):
        
        user = request.user
        new_parcela = request.data.copy()  # Crie uma cópia dos dados do request
        
        # Atribua o usuário autenticado aos campos 'created_by' e 'updated_by'
        new_parcela['created_by'] = user.id
        new_parcela['updated_by'] = user.id
        
        # Serializar os dados recebidos
        serializer = ParcelaSerializer(data=new_parcela)

        # Verifique se os dados são válidos
        if serializer.is_valid():
            serializer.save()  # Salve o novo objeto no banco de dados
            return Response(serializer.data, status=status.HTTP_201_CREATED)
       
        # Se os dados não forem válidos, retorne os detalhes dos erros
        return Response({
            "errors": serializer.errors, 
            "message": "Erro ao validar os dados de entrada."
        }, status=status.HTTP_400_BAD_REQUEST)
        
# @api_view(['GET'])
# def get_conta(request):
#     if(request.method == 'GET'):
#         contas = Conta.objects.all()
#         serializer = ContaSerializer(contas, many=True)
#         return Response(serializer.data)
    
#     return Response(status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET'])
# def get_finance(request):
#     if(request.method == 'GET'):
#         finances = Finance.objects.all()
#         serializer = FinanceSerializer(finances, many=True)
#         return Response(serializer.data)
    
#     return Response(status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET'])
# def get_parcela(request):
#     if(request.method == 'GET'):
#         parcelas = Parcela.objects.all()
#         serializer = ParcelaSerializer(parcelas, many=True)
#         return Response(serializer.data)
    
#     return Response(status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET'])
# def get_finance_entry(request):
#     if(request.method == 'GET'):
#         finance_entrys = FinanceEntry.objects.all()
#         serializer = FinanceEntrySerializer(finance_entrys, many=True)
#         return Response(serializer.data)
    
#     return Response(status=status.HTTP_400_BAD_REQUEST)