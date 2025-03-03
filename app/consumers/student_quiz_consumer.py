import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async as sync_to_async, aclose_old_connections

class StudentQuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f"live_quiz_{self.room_code}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        #await aclose_old_connections()

    async def disconnect(self, close_code):
        # Leave the quiz room
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        await aclose_old_connections()


    async def receive(self, text_data):
        # Use json.loads() to parse the JSON string into a dictionary
        data = json.loads(text_data)  # Changed from json.dumps(text_data)
        action = data.get('action')

        if "question" in data and "options" in data:
            # Correctly received question, update UI
            await self.send(text_data=json.dumps(data))
        else:
            # Debug: Message is missing question/options
            print("Received message missing question/options:", data)
        
        # Handle student actions like submitting an answer
        if action == "next_question":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "request_next_question",
                    "sender": self.channel_name
                }
            )

    async def quiz_update(self, event):
        print(f"Student received quiz update: {event}")
        message = event["message"]
        
        # Send the new question to the student's browser
        await self.send(text_data=json.dumps({
            "question": message["question"],
            "options": message["options"],
            "question_number": message["question_number"],
        }))
        await aclose_old_connections()
    
    # Additional handlers for other message types
    async def send_participants(self, event):
        await self.send(text_data=json.dumps({
            "participants": event["participants"]
        }))
