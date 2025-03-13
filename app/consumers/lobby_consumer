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

    @sync_to_async
    def get_participants(self, room):
        return list(room.participants.values_list('user__email_address', flat=True))

    async def send_updated_participants(self):
        from app.models.room import Room

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

    async def send_participants(self, event):
        await self.send(text_data=json.dumps({
            "participants": event["participants"]
        }))
    
    async def quiz_started(self, event):
        await self.send(text_data=json.dumps({
            "action": "quiz_started",
            "student_quiz_url": event.get("student_quiz_url"),
            "tutor_quiz_url": event.get("tutor_quiz_url")
        }))


class StudentQuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'quiz_{self.room_code}'

        # Join the quiz room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await aclose_old_connections()

    async def disconnect(self, close_code):
        # Leave the quiz room
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        await aclose_old_connections()

    # Receive broadcasted message from Tutor
    async def quiz_update(self, event):
        await self.send(text_data=json.dumps(event['message']))

        await aclose_old_connections()

        


# class TutorQuizConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_code = self.scope['url_route']['kwargs']['room_code']
#         self.room_group_name = f'quiz_{self.room_code}'

#         # Join the quiz room
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave the quiz room
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     # Receive message from tutor and broadcast it to students
#     async def receive(self, text_data):
#         data = json.loads(text_data)

#         # Extract the question and options sent by the tutor
#         question = data.get('question')
#         options = data.get('options')

#         # Broadcast to all students in the quiz room
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'quiz_update',  # This triggers quiz_update in StudentQuizConsumer
#                 'message': {
#                     'question': question,
#                     'options': options
#                 }
#             }
#         )
