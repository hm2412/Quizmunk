import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from app.models import Room
from app.models.quiz import (TrueFalseQuestion, IntegerInputQuestion, TextInputQuestion, DecimalInputQuestion, MultipleChoiceQuestion, NumericalRangeQuestion, SortingQuestion)
from app.models.responses import (TrueFalseResponse, IntegerInputResponse, TextInputResponse, DecimalInputResponse, MultipleChoiceResponse, NumericalRangeResponse, SortingResponse)


class StudentQuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.join_code = self.scope['url_route']['kwargs']['join_code']
        self.room = await database_sync_to_async(Room.objects.get)(join_code=self.join_code)
        self.room_group_name = f"student_{self.join_code}"
        self.answered_questions = set()
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
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
            if user and question_id:
                await self.save_response(user, question_type, question_id, answer)
            await self.channel_layer.group_send(
                f"live_quiz_{self.join_code}",
                {"type": "answer_received", "answer": answer}
            )
        elif action == "update":
            pass
    
    @database_sync_to_async
    def save_response(self, user, question_type, question_id, answer):
        if question_type == "true_false":
            question = TrueFalseQuestion.objects.get(id=question_id)
            return TrueFalseResponse.objects.create(player=user, room=self.room, question=question, answer=bool(answer))
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
        elif question_type == "sorting":
            question = SortingQuestion.objects.get(id=question_id)
            # If answer is sent as a list, convert it to a comma-separated string.
            answer_str = ",".join(answer) if isinstance(answer, list) else answer
            return SortingResponse.objects.create(player=user, room=self.room, question=question, answer=answer_str)
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
            "items": event.get("message").get("items", [])
        }
        await self.send(text_data=json.dumps(response))
    
    async def quiz_update(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def leaderboard_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "leaderboard_update",
            "leaderboard": event.get("leaderboard")
        }))
    

    async def quiz_ended(self, event):
        await self.send(text_data=json.dumps({
            "type": "quiz_ended",
            "message": event.get("message")
        }))