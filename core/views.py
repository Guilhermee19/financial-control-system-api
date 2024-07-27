from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from django.utils import timezone

from .models import User, Tag, Conta, Finance, Parcela, FinanceEntry
from .serializers import UserSerializer, TagSerializer, ContaSerializer, FinanceSerializer, ParcelaSerializer, FinanceEntrySerializer

import json


#?  ----------------------
#?  ------- USERS --------
#?  ----------------------
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
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)
    
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
def get_all_finances(request):
    if(request.method == 'GET'):
        finances = Finance.objects.all()
        serializer = FinanceSerializer(finances, many=True)
        return Response(serializer.data)
    
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