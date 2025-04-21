from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from core.models import Category
from core.serializers import CategorySerializer


class CategoryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        status_filter = request.query_params.get('status')
        name_filter = request.query_params.get('name')
        
        categories = Category.objects.filter(created_by=request.user)

        if status_filter == 'active':
            categories = categories.filter(is_active=True)
        elif status_filter == 'inactive':
            categories = categories.filter(is_active=False)

        if name_filter:
            categories = categories.filter(name__icontains=name_filter)

        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 10)
        result_page = paginator.paginate_queryset(categories, request)
        serializer = CategorySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        data = request.data.copy()
        data['created_by'] = request.user.id
        data['updated_by'] = request.user.id
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({
            "errors": serializer.errors,
            "message": "Erro ao validar os dados da categoria."
        }, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response({"worked": True})

    @action(detail=False, methods=["get"])
    def by_id(self, request):
        category_id = request.GET.get("id")
        if not category_id:
            return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
