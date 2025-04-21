from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from core.models import Card
from core.serializers import CardSerializer


class CardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        cards = Card.objects.filter(created_by=request.user)

        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 10)
        result_page = paginator.paginate_queryset(cards, request)

        serializer = CardSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        user = request.user
        data = request.data.copy()

        data['created_by'] = user.id
        data['updated_by'] = user.id
        data['is_active'] = True  # Define como ativo ao criar

        serializer = CardSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({
            "errors": serializer.errors,
            "message": "Erro ao validar os dados do cartão."
        }, status=status.HTTP_400_BAD_REQUEST)
