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

        print(f"Tutor joined group: {self.room_group_name}")

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        await self.send_updated_participants()

        mock_question = {
            'question': 'What is 2 + 2?',
            'options': ['3', '4', '5', '6']
        }
        await self.send(text_data=json.dumps(mock_question))

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

        if data.get("action") == "start_quiz":
    # Assuming you have a method that fetches the first question
            room = await sync_to_async(Room.objects.get)(join_code=self.join_code)
            quiz = room.quiz  # Assuming quiz is linked with the room

            first_question = await sync_to_async(self.get_next_question)(quiz)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "quiz_update",
                    "message": {
                        "question": first_question.text,
                        "options": first_question.options,
                        "question_number": 1
                    }
                }
            )

            

    

        # WHEN CREATING REAL QUESTIONS FUNCTIONALITY ADDED REPLACE THE MOCK DATA WITH BELOW CODE i.e. UNCOMMENT IT

        if data.get("action") == "next_question":
            # Get the current quiz based on the join_code (or room_code)
            room = await sync_to_async(Room.objects.get)(join_code=self.join_code)
            quiz = room.quiz  # (assuming the Room model has a ForeignKey to the Quiz model)

            # Get the next question for the quiz dynamically
            current_question = quiz.questions.first()  # Or fetch based on some logic
    
            next_question = await sync_to_async(self.get_next_question)(quiz, current_question)

            if not next_question:
                # End of quiz
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "quiz_update",
                        "message": {
                            "question": "The quiz has ended",
                            "options": [],
                            "question_number": -1
                        }
                    }
                )
                return

            # Send the next question
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "quiz_update",
                    "message": {
                        "question": next_question.text,
                        "options": next_question.options,
                        "question_number": quiz.get_question_number(next_question)
                    }
                }
            )

            



        # if data.get("action") == "next_question":
        #     mock_next_question = {
        #         'question': 'What is the capital of France?',
        #         'options': ['Berlin', 'Madrid', 'Paris', 'Rome']
        #     }
        #     await self.send(text_data=json.dumps(mock_next_question))

        
        

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

    def get_next_question(self, quiz, current_question):
    # Fetch the next question based on the current question's position
        next_question = quiz.questions.filter(order__gt=current_question.order).first()
        return next_question
    
    async def quiz_update(self, event):
        message = event["message"]
        print(f"Tutor sending quiz update: {message}")

        await self.send(text_data=json.dumps(message))


        # # Send the updated question to the client
        # await self.send(text_data=json.dumps({
        #     "question": message["question"],
        #     "options": message["options"],
        #     "question_number": message["question_number"]
        # }))

    

