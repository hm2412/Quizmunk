import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from app.models import RoomParticipant, GuestAccess, Room


class StudentQuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.join_code = self.scope['url_route']['kwargs']['join_code']
        self.room = await database_sync_to_async(Room.objects.get)(join_code=self.join_code)
        self.room_group_name = f"student_{self.join_code}"
        self.answered_questions = set()
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        self.user = self.scope.get("user")
        self.session = self.scope["session"]

        if self.user and self.user.is_authenticated and self.user.role.lower() != "tutor":
            await database_sync_to_async(RoomParticipant.objects.get_or_create)(
                room=self.room, user=self.user
            )
        else:
            guest_session = self.session.session_key
            if not guest_session:
                self.scope["session"].save()
                guest_session = self.scope["session"].session_key
            guest_access, _ = await database_sync_to_async(GuestAccess.objects.get_or_create)(
                session_id=guest_session
            )
            await database_sync_to_async(RoomParticipant.objects.get_or_create)(
                room=self.room, guest_access=guest_access
            )
        participants = await self.get_participants(self.room)
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
        from app.models import Room, RoomParticipant, GuestAccess
        room = await database_sync_to_async(Room.objects.get)(join_code=self.join_code)
        try:
            if self.user and self.user.is_authenticated:
                participant = await database_sync_to_async(RoomParticipant.objects.get)(
                    room=room, user_id=self.user.id
                )
            else:
                guest = await database_sync_to_async(GuestAccess.objects.get)(
                    session_id=self.session.session_key
                )
                participant = await database_sync_to_async(RoomParticipant.objects.get)(
                    room=room, guest_access=guest
                )
            #await database_sync_to_async(lambda: RoomParticipant.objects.filter(id=participant.id).delete())()
        except RoomParticipant.DoesNotExist:
            pass
        participants = await self.get_participants(room)
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
                return NumericalRangeResponse.objects.create(player=user, room=self.room, question=question, answer=float(answer))
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
                return NumericalRangeResponse.objects.create(guest_access=guest_access, room=self.room, question=question, answer=float(answer))
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


    @database_sync_to_async
    def get_participants(self, room):
        participants = room.participants.exclude(user__role__iexact="tutor")
        result = []
        for participant in participants:
            if participant.guest_access:
                result.append(f"Guest ({participant.guest_access.session_id[:8]})")
            else:
                result.append(participant.user.email_address)
        return result


    async def participants_update(self, event):
        await self.send(text_data=json.dumps({
            "action": "update_participants",
            "participant_number": event.get("participant_number"),
            "participants": event.get("participants")
        }))

    async def show_stats(self, event):
         stats_data = {
             "type": "show_stats",
             "correct_answer": event.get("correct_answer", ""),
             "responses_received": event.get("responses_received", -2),
             "correct_responses": event.get("correct_responses", -2),
         }
         await self.send(text_data=json.dumps(stats_data))
