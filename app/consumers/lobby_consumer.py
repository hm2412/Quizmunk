# Original implementation by Kyran and Areeb
#refactored by Tameem 14/3/2025
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async as sync_to_async, aclose_old_connections


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
        elif data.get("action") == "quiz_started":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "action": "quiz_started",
                    "student_quiz_url": data.get("student_quiz_url"),
                    "tutor_quiz_url": data.get("tutor_quiz_url"),
                }
            )
        else:
            await self.send(text_data=json.dumps({"error": "Unknown action in lobby"}))


    @sync_to_async
    def get_participants(self, room):
        participants = room.participants.exclude(user__role="tutor")
        result = []
        for participant in participants:
            if participant.guest_access:
                result.append(f"Guest ({participant.guest_access.session_id[:8]})")
            else:
                result.append(participant.user.email_address)
        return result


    async def send_updated_participants(self):
        from app.models import Room
        try:
            room = await sync_to_async(Room.objects.get)(join_code=self.join_code)
            participants = await self.get_participants(room)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "participants_update",
                    "participants": participants
                }
            )
        except Room.DoesNotExist:
            return


    async def participants_update(self, event):
        await self.send(text_data=json.dumps({
            "action": "update_participants",
            "participants": event["participants"]
        }))
    

    async def quiz_started(self, event):
        await self.send(text_data=json.dumps({
            "action": "quiz_started",
            "student_quiz_url": event["student_quiz_url"],
            "tutor_quiz_url": event["tutor_quiz_url"],
        }))