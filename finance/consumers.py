import json
from channels.generic.websocket import AsyncWebsocketConsumer
# from core.models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        print(self.user)
        
        self.group_name = f'user_{self.user.id}'

        # Adicione o usuário ao grupo de WebSocket
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Recebe mensagens do WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        event = text_data_json.get("event")
        user = self.scope['user']  # Assume que o usuário está autenticado
        print(user)
        # Log para verificar a mensagem recebida
        print(f"Recebido evento: {event}")

        if event == "notification":
            # Extraindo a mensagem do texto recebido
            data = text_data_json.get("data", "")  # Pega a mensagem ou uma string vazia se não existir
            message = data.get("message", "")  # Pega a mensagem ou uma string vazia se não existir
            await self.send_notification(message)


    # Envia uma notificação para o WebSocket
    async def send_notification(self, message):
        # Enviar a mensagem para o grupo
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'notification_message',
                'message': message
            }
        )


    # Recebe mensagens de outros grupos
    async def notification_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"event": "notification", "data": {"message": message}}))

