# finance/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from finance.consumers import NotificationConsumer
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('ws/notifications/', NotificationConsumer.as_asgi()),
        ])
    ),
})
