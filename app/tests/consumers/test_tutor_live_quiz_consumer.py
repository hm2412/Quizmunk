import json

from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from app.models import Room, RoomParticipant, GuestAccess, Quiz, IntegerInputQuestion
from app.consumers.tutor_live_quiz_consumer import TutorQuizConsumer

User = get_user_model()


class TutorQuizConsumerTests(TransactionTestCase):
    def setUp(self):
        # Create test data
        self.tutor = User.objects.create_user(
            email_address="tutor@example.com",
            first_name="Tu",
            last_name="Tor",
            password="password123",
            role="tutor"
        )
        self.quiz = Quiz.objects.create(
            tutor=self.tutor
        )
        self.room = Room.objects.create(
            join_code="ABCD1234",
            name="Test Room",
            quiz=self.quiz,
        )
        self.question = IntegerInputQuestion.objects.create(
            quiz=self.quiz,
            question_text="Test question",
            correct_answer=4,
            mark=10,
        )

    async def test_connection(self):
        communicator = WebsocketCommunicator(
            TutorQuizConsumer.as_asgi(),
            f"/ws/student_quiz/ABCD1234/"
        )
        communicator.scope['user'] = self.tutor
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.disconnect()

    # async def test_receive_start_quiz(self):
    #     communicator = WebsocketCommunicator(
    #         TutorQuizConsumer.as_asgi(),
    #         f"/ws/student_quiz/ABCD1234/"
    #     )
    #     communicator.scope['user'] = self.tutor
    #     communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}
    #
    #     await communicator.send_json_to({
    #         "action": "quiz_started",
    #         "student_quiz_url": "/student/live-quiz/ABCD1234/",
    #         "tutor_quiz_url": "/live-quiz/1/ABCD1234/"
    #     })
    #
    #     response = None
    #     while True:
    #         pass
