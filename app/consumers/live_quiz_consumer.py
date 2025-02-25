import json

from channels.generic.websocket import AsyncWebsocketConsumer
from app.models import Room
from channels.db import database_sync_to_async as sync_to_async, aclose_old_connections

class QuizConsumer(AsyncWebsocketConsumer):
    @sync_to_async
    def get_participants(self, room):
        return list(room.participants.values_list('user__email_address', flat=True))

    # Manage initial request when first connecting with client
    async def connect(self):
        self.join_code = self.scope['url_route']['kwargs']['join_code']
        self.room_group_name = f"live_quiz_{self.join_code}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        await self.send_updated_participants()

    # Manage clients disconnecting
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Manage messages received by client
    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get("action") == "update":
            await self.send_updated_participants()

    # Updating the participants in the channel
    async def send_updated_participants(self):
        try:
            room = await sync_to_async(Room.objects.get)(join_code=self.join_code)
            participants = await self.get_participants(room)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_participants",
                    "participants": participants
                }
            )
        except Room.DoesNotExist:
            return

    # Adding participants to the channel
    async def send_participants(self, event):
        await self.send(text_data=json.dumps({
            "participants": event["participants"]
        }))