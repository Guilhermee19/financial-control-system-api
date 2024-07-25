from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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
        serializer = UserSerializer(new_user)

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
        serializer = TagSerializer(new_tag)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
       
        return Response(status=status.HTTP_400_BAD_REQUEST)



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