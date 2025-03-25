# Original implementation by Kyran and Areeb
#refactored by Tameem 14/3/2025
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from app.models import RoomParticipant, GuestAccess


class StudentQuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.join_code = self.scope['url_route']['kwargs']['join_code']
        from app.models import Room
        self.room = await database_sync_to_async(Room.objects.get)(join_code=self.join_code)
        self.room_group_name = f"student_{self.join_code}"
        self.answered_questions = set()
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        self.user = self.scope.get("user")
        self.session = self.scope["session"]
        participants = await database_sync_to_async(list)(
            self.room.participants.exclude(user__role__iexact="tutor").values_list('user__email_address', flat=True)
        )
        participant_number = len(participants)
        update_message = {
            "type": "participants_update",
            "participants": participants,
            "participant_number": participant_number
        }
        await self.channel_layer.group_send(self.room_group_name, update_message)
        await self.channel_layer.group_send(f"live_quiz_{self.join_code}", update_message)


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        from app.models import Room
        room = await database_sync_to_async(Room.objects.get)(join_code=self.join_code)

        if self.user and self.user.is_authenticated:
            # When user is logged in
            participant = await database_sync_to_async(RoomParticipant.objects.get)(user_id=self.user.id)
        else:
            # When user is a guest
            guest = await database_sync_to_async(GuestAccess.objects.get)(session_id=self.session.session_key)
            participant = await database_sync_to_async(RoomParticipant.objects.get)(guest_access=guest)

        await database_sync_to_async(lambda: RoomParticipant.objects.filter(id=participant.id).delete())() # Removing the user from the participants

        participants = await database_sync_to_async(list)(
            room.participants.exclude(user__role__iexact="tutor").values_list('user__email_address', flat=True)
        )
        participant_number = len(participants)
        update_message = {
            "type": "participants_update",
            "participants": participants,
            "participant_number": participant_number
        }
        await self.channel_layer.group_send(self.room_group_name, update_message)
        await self.channel_layer.group_send(f"live_quiz_{self.join_code}", update_message)


    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        if action == "submit_answer":
            question_number = data.get("question_number")
            answer = data.get("answer")
            question_id = data.get("question_id")
            question_type = data.get("question_type")

            if question_id in self.answered_questions:
                return
            self.answered_questions.add(question_id)
            user = self.scope.get("user")
            await self.save_response(user, question_type, question_id, answer)
            await self.channel_layer.group_send(
                f"live_quiz_{self.join_code}",
                {"type": "answer_received", "answer": answer}
            )
        elif action == "update":
            pass


    @database_sync_to_async
    def save_response(self, user, question_type, question_id, answer):
        from app.models.quiz import TrueFalseQuestion, IntegerInputQuestion, TextInputQuestion, DecimalInputQuestion, MultipleChoiceQuestion, NumericalRangeQuestion
        from app.models.responses import TrueFalseResponse, IntegerInputResponse, TextInputResponse, DecimalInputResponse, MultipleChoiceResponse, NumericalRangeResponse
        if user.is_authenticated:
            if question_type == "true_false":
                question = TrueFalseQuestion.objects.get(id=question_id)
                bool_answer = True if str(answer).strip().lower() == "true" else False
                return TrueFalseResponse.objects.create(player=user, room=self.room, question=question, answer=bool_answer)
            elif question_type == "integer":
                question = IntegerInputQuestion.objects.get(id=question_id)
                return IntegerInputResponse.objects.create(player=user, room=self.room, question=question, answer=int(answer))
            elif question_type == "text":
                question = TextInputQuestion.objects.get(id=question_id)
                return TextInputResponse.objects.create(player=user, room=self.room, question=question, answer=answer)
            elif question_type == "decimal":
                question = DecimalInputQuestion.objects.get(id=question_id)
                return DecimalInputResponse.objects.create(player=user, room=self.room, question=question, answer=answer)
            elif question_type == "multiple_choice":
                question = MultipleChoiceQuestion.objects.get(id=question_id)
                return MultipleChoiceResponse.objects.create(player=user, room=self.room, question=question, answer=answer)
            elif question_type == "numerical_range":
                question = NumericalRangeQuestion.objects.get(id=question_id)
                return NumericalRangeResponse.objects.create(player=user, room=self.room, question=question, answer=answer)
            else:
                return None
        else:
            session_key = self.scope["session"].session_key
            from app.models import GuestAccess
            guest_access = GuestAccess.objects.get(session_id=session_key)
            if question_type == "true_false":
                question = TrueFalseQuestion.objects.get(id=question_id)
                bool_answer = True if str(answer).strip().lower() == "true" else False
                return TrueFalseResponse.objects.create(guest_access=guest_access, room=self.room, question=question, answer=bool_answer)
            elif question_type == "integer":
                question = IntegerInputQuestion.objects.get(id=question_id)
                return IntegerInputResponse.objects.create(guest_access=guest_access, room=self.room, question=question, answer=int(answer))
            elif question_type == "text":
                question = TextInputQuestion.objects.get(id=question_id)
                return TextInputResponse.objects.create(guest_access=guest_access, room=self.room, question=question, answer=answer)
            elif question_type == "decimal":
                question = DecimalInputQuestion.objects.get(id=question_id)
                return DecimalInputResponse.objects.create(guest_access=guest_access, room=self.room, question=question, answer=answer)
            elif question_type == "multiple_choice":
                question = MultipleChoiceQuestion.objects.get(id=question_id)
                return MultipleChoiceResponse.objects.create(guest_access=guest_access, room=self.room, question=question, answer=answer)
            elif question_type == "numerical_range":
                question = NumericalRangeQuestion.objects.get(id=question_id)
                return NumericalRangeResponse.objects.create(guest_access=guest_access, room=self.room, question=question, answer=answer)
            else:
                return None


    async def student_question(self, event):
        response = {
            "type": "question_update",
            "question": event.get("message").get("question"),
            "question_id": event.get("message").get("question_id"),
            "options": event.get("message").get("options"),
            "question_number": event.get("message").get("question_number"),
            "total_questions": event.get("message").get("total_questions"),
            "time": event.get("message").get("time"),
            "question_type": event.get("message").get("question_type", "multiple_choice"),
            "items": event.get("message").get("items", []),
            "image": event.get("message").get("image", "")
        }
        await self.send(text_data=json.dumps(response))


    async def quiz_update(self, event):
        await self.send(text_data=json.dumps(event))


    async def leaderboard_update(self, event):
        response = {
            "type": "leaderboard_update",
            "leaderboard": event.get("leaderboard")
        }
        if "answered_count" in event:
            response["answered_count"] = event["answered_count"]
        if "participant_number" in event:
            response["participant_number"] = event["participant_number"]
        await self.send(text_data=json.dumps(response))


    async def quiz_ended(self, event):
        await self.send(text_data=json.dumps({
            "type": "quiz_ended",
            "message": event.get("message")
        }))


    async def participants_update(self, event):
        await self.send(text_data=json.dumps({
            "action": "update_participants",
            "participant_number": event.get("participant_number"),
            "participants": event.get("participants")
        }))