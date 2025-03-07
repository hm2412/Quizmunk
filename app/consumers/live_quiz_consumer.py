import json

from channels.generic.websocket import AsyncWebsocketConsumer
from app.models import Room, RoomParticipant, GuestAccess
from channels.db import database_sync_to_async as sync_to_async, aclose_old_connections

class QuizConsumer(AsyncWebsocketConsumer):
    @sync_to_async
    def get_participants(self, room):
        return list(room.participants.values_list('user__email_address', flat=True))

    # Manage initial request when first connecting with client
    async def connect(self):
        self.join_code = self.scope['url_route']['kwargs']['join_code']
        self.room_group_name = f"live_quiz_{self.join_code}"

        print(f"Someone has joined the room: {self.room_group_name}")

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        await self.send_updated_participants()

        self.user = self.scope.get("user")
        self.session = self.scope["session"]
        print(f"User ID: {self.user.id}\nSession: {self.session.session_key}")

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

        if self.user and self.user.is_authenticated:
            # When user is logged in
            participant = await sync_to_async(RoomParticipant.objects.get)(user_id=self.user.id)
        else:
            # When user is a guest
            guest = await sync_to_async(GuestAccess.objects.get)(session_id=self.session.session_key)
            participant = await sync_to_async(RoomParticipant.objects.get)(guest_access=guest)

        await sync_to_async(lambda: RoomParticipant.objects.filter(id=participant.id).delete())() # Removing the user from the participants

        await self.send_updated_participants()

        await aclose_old_connections()

    # Manage messages received by client
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if "question" in data and "options" in data:
            # Correctly received question, update UI
            await self.send(text_data=json.dumps(data))
        else:
            # Debug: Message is missing question/options
            print("Received message missing question/options:", data)

        if action == "update":
            await self.send_updated_participants()

        elif action == "start_quiz":
            room = await sync_to_async(Room.objects.get)(join_code=self.join_code)

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

        # Handle student actions like submitting an answer
        elif action == "submit_answer":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "request_next_question",
                    "sender": self.channel_name
                }
            )

        # WHEN CREATING REAL QUESTIONS FUNCTIONALITY ADDED REPLACE THE MOCK DATA WITH BELOW CODE i.e. UNCOMMENT IT

        elif data.get("action") == "next_question":
            # Get the current quiz based on the join_code (or room_code)
            room = await sync_to_async(Room.objects.get)(join_code=self.join_code)
            quiz = room.quiz

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
            participantNumber = len(participants)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_participants",
                    "participants": participants,
                    "participant_number": participantNumber,
                }
            )
        except Room.DoesNotExist:
            return

    # Adding participants to the channel
    async def send_participants(self, event):
        await self.send(text_data=json.dumps({
            "participants": event["participants"],
            "participant_number": event["participant_number"]
        }))

    def get_next_question(self, quiz, current_question):
    # Fetch the next question based on the current question's position
        next_question = quiz.questions.filter(order__gt=current_question.order).first()
        return next_question
    
    async def quiz_update(self, event):
        message = event["message"]
        print(f"Quiz was updated: {message}")

        # Send the new question to the student's browser
        await self.send(text_data=json.dumps({
            "question": message["question"],
            "options": message["options"],
            "question_number": message["question_number"],
        }))
        await aclose_old_connections()


        # # Send the updated question to the client
        # await self.send(text_data=json.dumps({
        #     "question": message["question"],
        #     "options": message["options"],
        #     "question_number": message["question_number"]
        # }))

    

