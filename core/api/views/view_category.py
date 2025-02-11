from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from core.models import  Category
from core.serializers import *

#?  -----------------------
#?  -------- CATERIES ---------
#?  -----------------------
@api_view(['GET'])
def get_all_categories(request):
    if request.method == 'GET':
        # Obtém os parâmetros de status e nome da requisição
        status_filter = request.query_params.get('status', None)  # status: 'active' ou 'all'
        name_filter = request.query_params.get('name', None)  # Nome para filtrar categorias
        
        # Filtra as categorias com base no status e no nome
        categories = Category.objects.filter(created_by=request.user)
        
        if status_filter == 'active':
            categories = categories.filter(is_active=True)
        elif status_filter == 'inactive':
            categories = categories.filter(is_active=False)
        
        if name_filter:
            categories = categories.filter(name__icontains=name_filter)  # Filtro por nome (case insensitive)

        # PAGINAÇÃO
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 10)
        paginator.page_query_param = 'page'
        
        # Serializa as categorias e aplica a paginação
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

