from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from core.serializers import *

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
        
        