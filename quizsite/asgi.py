"""
ASGI config for quizsite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizsite.settings')

#application = get_asgi_application()

def get_websocket_url_patterns(): #delaying import
    from app.routing import websocket_urlpatterns
    return websocket_urlpatterns

application = ProtocolTypeRouter({
    'http':get_asgi_application(),
    'websocket':AuthMiddlewareStack(
        URLRouter(
            get_websocket_url_patterns()
        )
    )
})
