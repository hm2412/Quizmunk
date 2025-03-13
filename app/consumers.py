# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from app.models import Room
from app.models.quiz import DecimalInputQuestion, IntegerInputQuestion, MultipleChoiceQuestion, NumericalRangeQuestion, SortingQuestion, TextInputQuestion, TrueFalseQuestion

class QuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.join_code = self.scope['url_route']['kwargs']['join_code']
        self.path = self.scope['path']
        
        if '/ws/lobby/' in self.path:
            self.room_group_name = f"lobby_{self.join_code}"
        elif '/ws/student/' in self.path:
            self.room_group_name = f"student_{self.join_code}"
        else:
            self.room_group_name = f"live_quiz_{self.join_code}"
        
            
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        if "lobby" in self.room_group_name:
            await self.send_updated_participants()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "update":
            await self.send_updated_participants()
        elif action == "submit_answer":
            question_number = data.get("question_number")
            answer = data.get("answer")
            # Process and validate the submitted answer here
            print(f"Student submitted answer for question {question_number}: {answer}")
        elif action == "start_quiz":
            await self.start_quiz()
        elif action == "next_question":
            await self.next_question()
        elif action == "end_question":
            await self.end_question()
        elif action == "end_quiz":
            await self.end_quiz()

    @database_sync_to_async
    def get_room(self):
        return Room.objects.get(join_code=self.join_code)

    # @database_sync_to_async
    # def get_question_data(self, question, room):
    #     question_data = {
    #         "question": question.question_text,
    #         "question_number": room.current_question_index + 1,
    #         "total_questions": len(room.get_questions()),
    #         "time": question.time,
    #     }
    #     if hasattr(question, 'multiple_choice_questions'):
    #         question_data["options"] = question.multiple_choice_questions.options
    #         question_data["type"] = "multiple_choice"
    #     elif hasattr(question, 'true_false_questions'):
    #         question_data["options"] = ["True", "False"]
    #         question_data["type"] = "true_false"
    #     elif hasattr(question, 'integer_questions'):
    #         question_data["type"] = "integer"
    #     elif hasattr(question, 'text_questions'):
    #         question_data["type"] = "text"
    #     elif hasattr(question, 'decimal_questions'):
    #         question_data["type"] = "decimal"
    #     elif hasattr(question, 'numerical_range_questions'):
    #         question_data["type"] = "numerical_range"
    #     elif hasattr(question, 'sorting_questions'):
    #         question_data["items"] = question.sorting_questions.get_items()
    #         question_data["type"] = "sorting"
        
    
    #     elif hasattr(question, 'correct_answer'):
    #         question_data["answer"] = str(question.correct_answer)
        
    #     print("Generated Question Data:", question_data)
        
    #     return question_data

    

    # @database_sync_to_async
    # def get_question_data(self, question, room):
    #     print(f"Processing question: {type(question)}")  # Debugging

    #     question_data = {
    #         "question": question.question_text,
    #         "question_number": room.current_question_index + 1,
    #         "total_questions": len(room.get_questions()),
    #         "time": question.time,
    #         "type": "unknown"  # Default type
    #     }

    #     if isinstance(question, MultipleChoiceQuestion):
    #         question_data["options"] = question.options
    #         question_data["type"] = "multiple_choice"
    #     elif isinstance(question, TrueFalseQuestion):
    #         question_data["options"] = ["True", "False"]
    #         question_data["type"] = "true_false"
    #     elif isinstance(question, IntegerInputQuestion):
    #         question_data["type"] = "integer"
    #     elif isinstance(question, TextInputQuestion):
    #         question_data["type"] = "text"
    #     elif isinstance(question, DecimalInputQuestion):
    #         question_data["type"] = "decimal"
    #     elif isinstance(question, NumericalRangeQuestion):
    #         question_data["type"] = "numerical_range"
    #     elif isinstance(question, SortingQuestion):
    #         question_data["items"] = question.get_items()
    #         question_data["type"] = "sorting"

    #     # Always include the answer if it exists
    #     if hasattr(question, 'correct_answer'):
    #         question_data["answer"] = str(question.correct_answer)

    #     print("Generated Question Data:", question_data)  # Print for debugging

    #     return question_data

    @database_sync_to_async
    def get_question_data(self, question, room):
        question_data = {
            "question": question.question_text,
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

        if hasattr(question, 'correct_answer'):
            question_data["answer"] = str(question.correct_answer)

        print("Generated Question Data:", question_data)
        return question_data
    





    @database_sync_to_async
    def update_room_and_get_question(self, increment=False):
        room = Room.objects.get(join_code=self.join_code)
        if increment:
            room.current_question_index += 1
        room.save()

        question = room.get_current_question()
        if question:
            return question, room
        return None, None

    @database_sync_to_async
    def get_participants(self, room):
        return list(room.participants.values_list('user__email_address', flat=True))

    async def start_quiz(self):
        room = await self.get_room()
        question, room = await self.update_room_and_get_question()
        if question:
            question_data = await self.get_question_data(question, room)
            await self.send_question_update(question_data)
            await self.send_student_question(question_data)

    async def next_question(self):
        question, room = await self.update_room_and_get_question(increment=True)
        if question:
            question_data = await self.get_question_data(question, room)
            await self.send_question_update(question_data)
            await self.send_student_question(question_data)
        else:
            await self.send_quiz_ended("No more questions")

    async def end_question(self):
        await self.send(text_data=json.dumps({"type": "end_question"}))

    async def end_quiz(self):
        await self.send_quiz_ended("Quiz has ended")

    async def send_updated_participants(self):
        try:
            room = await database_sync_to_async(Room.objects.get)(join_code=self.join_code)
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

    async def send_question_update(self, question_data):
        print(f"Sending question update: {question_data}")
        await self.send(text_data=json.dumps({
            "type": "question_update",
            **question_data
        }))

    async def send_quiz_ended(self, message):
        await self.send(text_data=json.dumps({
            "type": "quiz_ended",
            "message": message
        }))

    async def quiz_started(self, event):
        await self.send(text_data=json.dumps({
            "action": "quiz_started",
            "student_quiz_url": event.get("student_quiz_url"),
            "tutor_quiz_url": event.get("tutor_quiz_url")
        }))

    
    async def send_student_question(self, question_data):
        print(f"Sending student question: {question_data}")
        await self.channel_layer.group_send(
            f"student_{self.join_code}",
            {
                "type": "student_question",
                "question": question_data["question"],
                "options": question_data.get("options", []),
                "question_type": question_data.get("question_type", "multiple_choice"), # Default value is multiple choice, but we are correcting the type in HTML/javascript!
                "items": question_data.get("items", []),
                "question_number": question_data["question_number"]
            }
        )

    def get_question_options(self, question_data):
        # Extract options based on question type
        if hasattr(question_data, 'options'):
            return question_data.options
        # Add other question type handling as needed
        return []
        
    async def student_question(self, event):
        await self.send(text_data=json.dumps({
            "type": "question_update",
            "question": event["question"],
            "options": event["options"],
            "question_type": event.get("question_type", None),  
            "items": event.get("items", []),    
            "question_number": event["question_number"]
        }))
