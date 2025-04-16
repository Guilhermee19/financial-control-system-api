from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import *

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()  # Certifique-se de que isso esteja definido
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtra as notificações do usuário autenticado
        return Notification.objects.filter(user=self.request.user).order_by('-timestamp')

    def list(self, request, *args, **kwargs):
        # Método para obter notificações
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # Método para criar notificações
        notification = serializer.save()
        channel_layer = get_channel_layer()
        # Envie a notificação pelo WebSocket
        async_to_sync(channel_layer.group_send)(
            f'user_{notification.user.id}',
            {
                'type': 'send_notification',
                'message': notification.message
            }
        )
        