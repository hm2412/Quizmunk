# Original implementation by Kyran and Areeb
#refactored by Tameem 14/3/2025
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async, aclose_old_connections
from app.helpers.helper_functions import get_all_responses_question, isCorrectAnswer
from asyncio import sleep

class TutorQuizConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_room(self, join_code):
        from app.models import Room
        return Room.objects.get(join_code=join_code)
    

    @database_sync_to_async
    def update_quiz_state(self, room, **kwargs):
        from app.models import QuizState
        qs, _ = QuizState.objects.get_or_create(room=room)
        for key, value in kwargs.items():
            setattr(qs, key, value)
        qs.save()
        return qs
    

    @database_sync_to_async
    def get_leaderboard(self, room):
        if not room:
            return []
        from app.models import RoomParticipant
        participants = RoomParticipant.objects.filter(room=room).exclude(user__role__iexact="tutor")
        for participant in participants:
            if participant.user:
                from app.helpers.helper_functions import calculate_user_score
                participant.score = calculate_user_score(participant.user, room)
            elif participant.guest_access:
                from app.helpers.helper_functions import calculate_guest_score
                participant.score = calculate_guest_score(participant.guest_access, room)
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
    def get_participants(self, room):
        participants = room.participants.exclude(user__role__iexact="tutor")
        result = []
        for participant in participants:
            if participant.guest_access:
                result.append(f"Guest ({participant.guest_access.session_id[:8]})")
            else:
                result.append(participant.user.email_address)
        return result

        #return list(room.participants.exclude(user__role__iexact="tutor").values_list('user__email_address', flat=True))
    
    @database_sync_to_async
    def get_question_stats(self, question, room):
        responses = get_all_responses_question(room, question)

        responses_received = responses.count()
        correct_responses = 0
        for response in responses:
            if isCorrectAnswer(response):
                correct_responses += 1

        if responses_received:
            return {
                "question_id": question.id,
                "responses_received": responses_received,
                "correct_responses": correct_responses
            }
        else:
            return {
                "question_id": question.id,
                "responses_received": 0,
                "correct_responses": 0
            }

    async def connect(self):
        self.join_code = self.scope['url_route']['kwargs']['join_code']
        self.room_group_name = f"live_quiz_{self.join_code}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        #await self.send_updated_participants()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await aclose_old_connections()


    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        user = self.scope.get("user")
        is_tutor = user.is_authenticated and getattr(user, "role", "").lower() == "tutor"
        if not is_tutor:
            await self.send(text_data=json.dumps({"error": "Only tutors can perform this action."}))
            return

        if action == "start_quiz":
            await self.handle_start_quiz()
        elif action == "end_question":
            await self.handle_end_question()
        elif action == "next_question":
            await self.handle_next_question()
        elif action == "end_quiz":
            await self.handle_end_quiz()
        elif action == "show_stats":
            await self.show_stats(data)
        else:
            await self.send(text_data=json.dumps({"error": "Unknown action"}))


    async def handle_start_quiz(self):
        room = await self.get_room(self.join_code)
        await self.update_quiz_state(room, current_question_index=0, quiz_started=True)
        question = await self.get_current_question(room)
        if question:
            question_data = await self.get_question_data(question, room, reveal_answer=False)
            await self.send_question_update(question_data)
            await self.send_student_question(question_data)
        else:
            await self.send(text_data=json.dumps({"error": "No question available"}))


    async def handle_end_question(self):
        room = await self.get_room(self.join_code)
        question = await self.get_current_question(room)
        if question:
            question_data = await self.get_question_data(question, room, reveal_answer=True)

            stats = await self.get_question_stats(question, room)
            responses_received = stats.get("responses_received", -1)
            correct_responses = stats.get("correct_responses", -1)

            await self.channel_layer.group_send(
                f"student_{self.join_code}",
                {
                    "type": "show_stats",
                    "correct_answer": question_data.get("answer", ""),
                    "responses_received": responses_received,
                    "correct_responses": correct_responses
                }
            )

            await self.send_question_update(question_data)
            await self.send_student_question(question_data)
        else:
            await self.send(text_data=json.dumps({"error": "No question to end"}))

    async def show_stats(self, event):
        await self.send(text_data=json.dumps({
            "type": "show_stats",
            "correct_answer": event.get("correct_answer", ""),
            "responses_received": event.get("responses_received", -2),
            "correct_responses": event.get("correct_responses", -2),
        }))

    async def handle_next_question(self):
        room = await self.get_room(self.join_code)
        next_q = await database_sync_to_async(room.next_question)()
        if next_q:
            question_data = await self.get_question_data(next_q, room, reveal_answer=False)
            await self.send_question_update(question_data)
            await self.send_student_question(question_data)
        else:
            from app.helpers.helper_functions import create_quiz_stats
            await database_sync_to_async(create_quiz_stats)(room)
            message = "No more questions!"
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "quiz_ended", "message": message}
            )
            await self.channel_layer.group_send(
                f"student_{self.join_code}",
                {"type": "quiz_ended", "message": message}
            )


    async def handle_end_quiz(self):
        room = await self.get_room(self.join_code)
        await self.update_quiz_state(room, current_question_index=-1, quiz_started=False)
        from app.helpers.helper_functions import create_quiz_stats
        await database_sync_to_async(create_quiz_stats)(room)
        await database_sync_to_async(room.save)()
        await self.send_quiz_ended("Quiz ended! Redirecting...")
        await self.channel_layer.group_send(
            f"student_{self.join_code}",
            {"type": "quiz_ended", "message": "Quiz ended! Redirecting..."}
        )
    
    async def send_quiz_ended(self, message):
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "quiz_ended", "message": message}
        )
    

    @database_sync_to_async
    def get_question_data(self, question, room, reveal_answer=False):
        question_data = {
            "question": question.question_text,
            "question_id": question.id,
            "question_number": room.current_question_index + 1,
            "total_questions": len(room.get_questions()),
            "time": question.time,
            "question_type": "unknown",
            "image": "/static/images/default_thumbnail.png"
        }

        if question.image:
            question_data["image"] = question.image.url

        from app.models import MultipleChoiceQuestion, TrueFalseQuestion, IntegerInputQuestion, TextInputQuestion, DecimalInputQuestion, NumericalRangeQuestion
        if isinstance(question, MultipleChoiceQuestion):
            question_data["options"] = question.options
            question_data["question_type"] = "multiple_choice"
        elif isinstance(question, TrueFalseQuestion):
            question_data["options"] = ["True", "False"]
            question_data["question_type"] = "true_false"
        elif isinstance(question, IntegerInputQuestion):
            question_data["options"] = []
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
        if reveal_answer and hasattr(question, "correct_answer"):
            question_data["answer"] = str(question.correct_answer)
            question_data["time"] = 0
        else:
            question_data["answer"] = ""
        return question_data
    

    async def send_question_update(self, question_data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "quiz_update", "message": question_data}
        )
    

    async def send_student_question(self, question_data):
        await self.channel_layer.group_send(
            f"student_{self.join_code}",
            {"type": "student_question", "message": question_data}
        )
    

    async def quiz_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "quiz_update",
            "message": event["message"]
        }))
        room = await self.get_room(self.join_code)
        leaderboard = await self.get_leaderboard(room)
        participants = await self.get_participants(room)
        participant_number = len(participants)
        
        current_question = await self.get_current_question(room)
        answered_count = 0
        if current_question:
            from app.helpers.helper_functions import count_answers_for_question
            answered_count = await database_sync_to_async(count_answers_for_question)(room, current_question)
        
        await self.send(text_data=json.dumps({
            "type": "leaderboard_update",
            "leaderboard": leaderboard,
            "participant_number": participant_number,
            "answered_count": answered_count
        }))


    async def answer_received(self, event):
        room = await self.get_room(self.join_code)
        leaderboard = await self.get_leaderboard(room)
        current_question = await self.get_current_question(room)
        answered_count = 0
        if current_question:
            from app.helpers.helper_functions import count_answers_for_question
            answered_count = await database_sync_to_async(count_answers_for_question)(room, current_question)
        update_payload = {
            "type": "leaderboard_update",
            "leaderboard": leaderboard,
            "answered_count": answered_count
        }
        await self.channel_layer.group_send(f"live_quiz_{self.join_code}", update_payload)
        await self.channel_layer.group_send(f"student_{self.join_code}", update_payload)


    async def send_updated_participants(self):
        try:
            from app.models import Room
            room = await database_sync_to_async(Room.objects.get)(join_code=self.join_code)
            participants = await self.get_participants(room)
            participant_number = len(participants)
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "participants_update", "participants": participants, "participant_number": participant_number}
            )
        except Exception as e:
            print("[UPDATE PARTICIPANTS] Error:", e)


    async def participants_update(self, event):
        await self.send(text_data=json.dumps({
            "action": "update_participants",
            "participants": event["participants"],
            "participant_number": event["participant_number"]
        }))


    async def quiz_ended(self, event):
        try:
            await self.send(text_data=json.dumps({
                "type": "quiz_ended",
                "message": event.get("message")
            }))
        except Exception:
            pass
    

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