from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import User, Tag, Conta, Finance, Parcela, FinanceEntry
from .serializers import UserSerializer, TagSerializer, ContaSerializer, FinanceSerializer, ParcelaSerializer, FinanceEntrySerializer
from rest_framework.pagination import PageNumberPagination
from datetime import datetime
from django.db.models import Q

import json
import httplib2
import certifi
import datetime

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user.is_active:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
            })
        else:
            return Response({'detail': 'Usuário inativo'}, status=status.HTTP_400_BAD_REQUEST)


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
def post_user(request):
    if(request.method == 'POST'):
        
        new_user = request.data
        serializer = UserSerializer(data=new_user)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
       
        return Response(status=status.HTTP_400_BAD_REQUEST)


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
        
        new_tag = request.data
        serializer = TagSerializer(data=new_tag)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
       
        return Response(status=status.HTTP_400_BAD_REQUEST)

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
        contas = Conta.objects.all()
        serializer = ContaSerializer(contas, many=True)
        return Response(serializer.data)
    
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
        
        new_conta = request.data
        serializer = ContaSerializer(data=new_conta)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
       
        return Response(status=status.HTTP_400_BAD_REQUEST)

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

        # Apply the date filter to the queryset
        finances = Finance.objects.filter(
            created_by      = request.user,
            created_at__gte = start_date,
            created_at__lt  = end_date
        )
        
        # PAGINATION
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 10)
        paginator.page_query_param = 'page'

        serializer = FinanceSerializer(paginator.paginate_queryset(finances, request), many=True).data
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
def post_finance(request):
    if(request.method == 'POST'):
        
        new_finance = request.data
        
        print(new_finance)
        
        # total_amount = request.data.get('value')
        # num_installments = request.data.get('number_of_installments')
        # installment_amount = float(total_amount) / int(num_installments)
        
        # # Validação
        # if not total_amount or not num_installments:
        #     return Response({'detail': 'Total amount and number of installments are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # print(installment_amount)
        
        serializer = FinanceSerializer(data=new_finance)
        
        if serializer.is_valid():
            serializer.save()
            
            # # Criar as parcelas
            # start_date = timezone.now().date()  # Data inicial pode ser a data atual
            # for i in range(int(num_installments)):
            #     due_date = start_date + timedelta(days=(i + 1) * 30)  # Parcelas mensais, ajuste conforme necessário
                
            #     Parcela.objects.create(
            #         finance=serializer.data.get('id'),
            #         installment_value=installment_amount,
            #         current_installment=i
            #         date=due_date
            #     )
                
                
            return Response(serializer.data, status=status.HTTP_201_CREATED)
       
        return Response(status=status.HTTP_400_BAD_REQUEST)

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