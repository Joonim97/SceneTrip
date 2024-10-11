"""
ASGI config for SceneTrip project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
import chats.routing  # 이제 이 코드는 안전하게 실행될 수 있습니다.

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SceneTrip.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": 
        AuthMiddlewareStack(
            AllowedHostsOriginValidator(
            URLRouter(
                chats.routing.websocket_urlpatterns
            )     
        ),
    ),
})