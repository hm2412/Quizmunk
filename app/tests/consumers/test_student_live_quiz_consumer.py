import json

from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from app.models import Room, RoomParticipant, GuestAccess
from app.consumers.student_live_quiz_consumer import StudentQuizConsumer

User = get_user_model()


class StudentQuizConsumerTests(TransactionTestCase):
    def setUp(self):
        # Create test data
        self.room = Room.objects.create(
            join_code="ABCD1234",
            name="Test Room"
        )
        self.student = User.objects.create_user(
            email_address="student@example.com",
            first_name="Stu",
            last_name="Dent",
            password="password123",
            role="student"
        )
        self.tutor = User.objects.create_user(
            email_address="tutor@example.com",
            first_name="Tu",
            last_name="Tor",
            password="password123",
            role="tutor"
        )

    async def test_authenticated_student_connection(self):
        communicator = WebsocketCommunicator(
            StudentQuizConsumer.as_asgi(),
            f"/ws/student_quiz/ABCD1234/"
        )
        communicator.scope['user'] = self.student
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_receive_answer_submission(self):
        communicator = WebsocketCommunicator(
            StudentQuizConsumer.as_asgi(),
            f"/ws/student_quiz/ABCD1234/"
        )
        communicator.scope['user'] = self.student
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}
        await communicator.connect()

        # Making a question in a quiz
        from app.models.quiz import Quiz
        quiz = await database_sync_to_async(Quiz.objects.create)(
            tutor=self.tutor
        )
        self.room.quiz = quiz

        from app.models.quiz import IntegerInputQuestion
        question = await database_sync_to_async(IntegerInputQuestion.objects.create)(
            quiz=quiz,
            question_text="Test question",
            correct_answer=4,
            mark=10,
        )

        # Making an answer
        test_answer = {
            "action": "submit_answer",
            "question_number": 1,
            "answer": 4,
            "question_id": question.id,
            "question_type": "integer",
        }

        await communicator.send_json_to(test_answer)

        # Finding the corresponding response
        from app.models.responses import IntegerInputResponse
        hasResponded = await database_sync_to_async(IntegerInputResponse.objects.filter(
            player=self.student,
            room=self.room,
            answer=4,
            question=question,
        ).exists)()

        self.assertTrue(hasResponded)
