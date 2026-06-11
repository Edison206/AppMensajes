import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AppMensajes.settings')

import django
django.setup()  # 🔥 ESTA LÍNEA ES LA CLAVE

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from Chats.consumers import ChatConsumer

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter([
        path("ws/chat/<int:chat_id>/", ChatConsumer.as_asgi()),
    ]),
})



# """
# ASGI config for AppMensajes project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
# """

# import os
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.core.asgi import get_asgi_application
# from django.urls import path
# from Chats.consumers import ChatConsumer  # asegúrate que "app" es correcto

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AppMensajes.settings')

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": URLRouter([
#         path("ws/chat/<int:chat_id>/", ChatConsumer.as_asgi()),
#     ]),
# })