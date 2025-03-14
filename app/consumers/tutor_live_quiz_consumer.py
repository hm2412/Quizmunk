# Original implementation by Areeb and Kyran
# Refactored by Tameem on 14/3/2025
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async, aclose_old_connections
from app.models import Room, RoomParticipant, QuizState
from app.models.quiz import DecimalInputQuestion, IntegerInputQuestion, MultipleChoiceQuestion, NumericalRangeQuestion, SortingQuestion, TextInputQuestion, TrueFalseQuestion
from app.helpers import helper_functions


class TutorQuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.join_code = self.scope['url_route']['kwargs']['join_code']
        self.room_group_name = f"live_quiz_{self.join_code}"
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.send_updated_participants()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await aclose_old_connections()


    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        user = self.scope.get("user")
        is_tutor = user.is_authenticated and getattr(user, "role", "").lower() == "tutor"
        if not is_tutor:
            await self.send(text_data=json.dumps({"error": "Only tutors can perform this action."}))
            return
        
        #check these later
        if action == "start_quiz":
            await self.start_quiz()
        elif action == "next_question":
            await self.next_question()
        elif action == "end_question":
            await self.end_question()
        elif action == "end_quiz":
            await self.end_quiz()
        else:
            await self.send(text_data=json.dumps({"error": "Unknown action"}))


    @database_sync_to_async
    def get_room(self):
        return Room.objects.get(join_code=self.join_code)


    @database_sync_to_async
    def get_question_data(self, question, room, reveal_answer=False):
        question_data = {
            "question": question.question_text,
            "question_id": question.id,
            "question_number": room.current_question_index + 1,
            "total_questions": len(room.get_questions()),
            "time": question.time,
            "question_type": "unknown"  # Default value
        }

        # Detect question type using isinstance
        if isinstance(question, MultipleChoiceQuestion):
            question_data["options"] = question.options
            question_data["question_type"] = "multiple_choice"
        elif isinstance(question, TrueFalseQuestion):
            question_data["options"] = ["True", "False"]
            question_data["question_type"] = "true_false"
        elif isinstance(question, IntegerInputQuestion):
            question_data["options"] = []  # No predefined options
            question_data["question_type"] = "integer"
        elif isinstance(question, TextInputQuestion):
            question_data["options"] = []
            question_data["question_type"] = "text"
        elif isinstance(question, DecimalInputQuestion):
            question_data["options"] = []
            question_data["question_type"] = "decimal"
        elif isinstance(question, NumericalRangeQuestion):
            question_data["options"] = []
            question_data["question_type"] = "numerical_range"
        elif isinstance(question, SortingQuestion):
            question_data["items"] = question.get_items()
            question_data["question_type"] = "sorting"

        if reveal_answer and hasattr(question, "correct_answer"):
            question_data["answer"] = str(question.correct_answer)
            question_data["time"] = 0
        
        return question_data


    @database_sync_to_async
    def update_quiz_state(self, room, **kwargs):
        qs, _ = QuizState.objects.get_or_create(room=room)
        for key, value in kwargs.items():
            setattr(qs, key, value)
        qs.save()
        return qs


    @database_sync_to_async
    def get_current_question(self, room):
        return room.get_current_question()

    
    @database_sync_to_async
    def get_participants(self, room):
        return list(room.participants.exclude(user__role__iexact="tutor").values_list('user__email_address', flat=True))


    async def start_quiz(self):
        room = await self.get_room(self.join_code)
        await self.update_quiz_state(room, current_question_index=0, quiz_started=True)
        question = await self.get_current_question(room)
        if question:
            question_data = await self.get_question_data(question, room, reveal_answer=False)
            await self.send_question_update(question_data)
            await self.send_student_question(question_data)
        else:
            await self.send(text_data=json.dumps({"error": "No question available"}))


    async def next_question(self):
        room = await self.get_room(self.join_code)
        next_q = await database_sync_to_async(room.next_question)()
        if next_q:
            question_data = await self.get_question_data(next_q, room, reveal_answer=False)
            await self.send_question_update(question_data)
            await self.send_student_question(question_data)
        else:
            await self.send_quiz_ended("No more questions")

    async def end_question(self):
        room = await self.get_room(self.join_code)
        question = await self.get_current_question(room)
        if question:
            question_data = await self.get_question_data(question, room, reveal_answer=True)
            await self.send_question_update(question_data)
            await self.send_student_question(question_data)
        else:
            await self.send(text_data=json.dumps({"error": "No question to end"}))


    async def end_quiz(self):
        room = await self.get_room(self.join_code)
        await self.update_quiz_state(room, current_question_index=-1, quiz_started=False)
        await self.send_quiz_ended("Quiz ended! Redirecting...")


    async def send_updated_participants(self):
        try:
            room = await database_sync_to_async(Room.objects.get)(join_code=self.join_code)
            participants = await self.get_participants(room)
            participant_number = len(participants)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_participants",
                    "participants": participants,
                    "participant_number": participant_number
                }
            )
        except Room.DoesNotExist:
            return


    async def send_participants(self, event):
        await self.send(text_data=json.dumps({
            "participants": event["participants"]
        }))


    async def send_question_update(self, question_data):
        await self.send(text_data=json.dumps({
            "type": "question_update",
            "message": question_data
        }))


    async def quiz_started(self, event):
        await self.send(text_data=json.dumps({
            "action": "quiz_started",
            "student_quiz_url": event.get("student_quiz_url"),
            "tutor_quiz_url": event.get("tutor_quiz_url")
        }))

    
    async def send_student_question(self, question_data):
        await self.channel_layer.group_send(
            f"student_{self.join_code}",
            {"type": "student_question", "message": question_data}
        )

    
    async def student_question(self, event):
        await self.send(text_data=json.dumps({
            "type": "question_update",
            "question": event["question"],
            "options": event["options"],
            "question_type": event.get("question_type", None),  
            "items": event.get("items", []),    
            "question_number": event["question_number"]
        }))

    
    @database_sync_to_async
    def get_leaderboard(self, room):
        participants = RoomParticipant.objects.filter(room=room).exclude(user__role__iexact="tutor")
        for participant in participants:
            if participant.user:
                participant.score = helper_functions.calculate_user_score(participant.user, room)
        RoomParticipant.objects.bulk_update(participants, ['score'])
        leaderboard_data = (
            participants.order_by('-score', 'joined_at')
            .values('user__email_address', 'guest_access__session_id', 'score')
        )
        return [
            {
                "rank": rank,
                "participant": participant["user__email_address"] or f"Guest ({participant['guest_access__session_id'][:8]})",
                "score": participant["score"]
            }
            for rank, participant in enumerate(leaderboard_data, start=1)
        ]
    

    @database_sync_to_async
    def get_current_question(self, room):
        return room.get_current_question()
    

    @database_sync_to_async
    def update_quiz_state(self, room, **kwargs):
        qs, _ = QuizState.objects.get_or_create(room=room)
        for key, value in kwargs.items():
            setattr(qs, key, value)
        qs.save()
        return qs
    

    async def send_quiz_ended(self, message):
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "quiz_ended", "message": message}
        )
    

    async def quiz_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "quiz_update",
            "message": event["message"]
        }))
        room = await self.get_room(self.join_code)
        leaderboard = await self.get_leaderboard(room)
        await self.send(text_data=json.dumps({
            "type": "leaderboard_update",
            "leaderboard": leaderboard
        }))

    
    async def answer_received(self, event):
        room = await self.get_room(self.join_code)
        leaderboard = await self.get_leaderboard(room)
        await self.channel_layer.group_send(
            f"live_quiz_{self.join_code}",
            {"type": "leaderboard_update", "leaderboard": leaderboard}
        )
        await self.channel_layer.group_send(
            f"student_{self.join_code}",
            {"type": "leaderboard_update", "leaderboard": leaderboard}
        )
    

    async def participants_update(self, event):
        await self.send(text_data=json.dumps({
            "action": "update_participants",
            "participants": event["participants"],
            "participant_number": event["participant_number"]
        }))  
    

    async def quiz_ended(self, event):
        await self.send(text_data=json.dumps({
            "type": "quiz_ended",
            "message": event.get("message")
        }))
    

    async def leaderboard_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "leaderboard_update",
            "leaderboard": event.get("leaderboard")
        }))