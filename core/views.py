from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import User, Tag, Conta, Finance, Parcela, FinanceEntry
from .serializers import UserSerializer, TagSerializer, ContaSerializer, FinanceSerializer, ParcelaSerializer, FinanceEntrySerializer

import json

# Create your views here.

@api_view(['GET'])
def get_user(request):
    if(request.method == 'GET'):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        
        return Response(serializer.data)
    
    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_tag(request):
    if(request.method == 'GET'):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        
        return Response(serializer.data)
    
    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_conta(request):
    if(request.method == 'GET'):
        contas = Conta.objects.all()
        serializer = ContaSerializer(contas, many=True)
        
        return Response(serializer.data)
    
    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_finance(request):
    if(request.method == 'GET'):
        finances = Finance.objects.all()
        serializer = FinanceSerializer(finances, many=True)
        
        return Response(serializer.data)
    
    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_parcela(request):
    if(request.method == 'GET'):
        parcelas = Parcela.objects.all()
        serializer = ParcelaSerializer(parcelas, many=True)
        
        return Response(serializer.data)
    
    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_finance_entry(request):
    if(request.method == 'GET'):
        finance_entrys = FinanceEntry.objects.all()
        serializer = FinanceEntrySerializer(finance_entrys, many=True)
        
        return Response(serializer.data)
    
    return Response(status=status.HTTP_404_NOT_FOUND)