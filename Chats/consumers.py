import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from .models import message, chat, User
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f"chat_{self.chat_id}"

        # unir al grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # salir del grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 🔥 recibir mensaje desde frontend
    async def receive(self, text_data):
        data = json.loads(text_data)
        mensaje = data['mensaje']
        user_id = data['user_id']

        nuevo_mensaje = await self.guardar_mensaje(user_id, mensaje)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'mensaje': nuevo_mensaje["texto"],
                'user': nuevo_mensaje["user"],
                'time': nuevo_mensaje["time"]
            }
        )

    # 🔥 enviar mensaje a frontend
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'mensaje': event['mensaje'],
            'user': event['user'],
            'time': event['time']
        }))

    @sync_to_async
    def guardar_mensaje(self, user_id, texto):
        user = User.objects.get(id=user_id)
        chat_obj = chat.objects.get(id=self.chat_id)

        mensaje = message.objects.create(
            user=user,
            chat=chat_obj,
            text_message=texto,
            view_message=False,
            resend_message=False
        )

        return {
            "texto": mensaje.text_message,
            "user": user.name_user,
            "time": str(mensaje.time_message)
        }