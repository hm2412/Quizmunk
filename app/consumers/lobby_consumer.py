import json
from channels.generic.websocket import AsyncWebsocketConsumer
from app.models import Room, RoomParticipant

class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.join_code = self.scope['url_route']['kwargs']['join_code']
        self.room_group_name = f"lobby_{self.join_code}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        await self.send_updated_participants()

    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        if data.get("action") == "update":
            await self.send_updated_participants()

    async def send_updated_participants(self):
        try:
            room = await Room.objects.aget(join_code=self.join_code)
            participants = list(room.participants.values_list('user__email_address', flat=True))

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_participants",
                    "participants": participants
                }
            )
        except Room.DoesNotExist:
            return  

    async def send_participants(self, event):
        await self.send(text_data=json.dumps({
            "participants": event["participants"]
        }))