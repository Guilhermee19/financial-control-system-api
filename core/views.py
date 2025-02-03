from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status
from .models import User, Category, Account, Transaction
from .serializers import *

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import json
import httplib2
import certifi

@api_view(['GET'])
@permission_classes([AllowAny])
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user)  # Filtrando as notificações do usuário
    serializer = NotificationSerializer(notifications, many=True)  # Passando o QuerySet com many=True
    return Response(serializer.data)  # Retornando os dados serializados

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

