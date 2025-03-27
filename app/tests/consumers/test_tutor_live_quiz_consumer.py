import json

from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from app.models import Room, RoomParticipant, GuestAccess, Quiz, IntegerInputQuestion, TrueFalseQuestion, \
    TextInputQuestion, DecimalInputQuestion, MultipleChoiceQuestion, NumericalRangeQuestion
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
        self.student = User.objects.create(
            first_name="John",
            last_name="Doe",
            email_address="johndoe@example.org"
        )
        self.quiz = Quiz.objects.create(
            tutor=self.tutor
        )
        self.empty_quiz = Quiz.objects.create(
            tutor=self.tutor
        )
        self.room = Room.objects.create(
            join_code="ABCD1234",
            name="Test Room",
            quiz=self.quiz,
        )
        self.empty_room = Room.objects.create(
            join_code="4321DCBA",
            name="Empty Room",
            quiz=self.empty_quiz,
        )
        self.integer_input_question = IntegerInputQuestion.objects.create(
            quiz=self.quiz,
            question_text="Test question",
            correct_answer=4,
            mark=10,
        )
        self.true_false_question = TrueFalseQuestion.objects.create(
            quiz=self.quiz,
            question_text="Test question",
            correct_answer=True,
            mark=10,
        )
        self.text_input_question = TextInputQuestion.objects.create(
            quiz=self.quiz,
            question_text="Test question",
            correct_answer="Correct",
            mark=10,
        )
        self.decimal_input_question = DecimalInputQuestion.objects.create(
            quiz=self.quiz,
            question_text="Test question",
            correct_answer=5.5,
            mark=10,
        )
        self.multiple_choice_question = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            question_text="Test question",
            options=["Incorrect 1", "Incorrect 2", "Incorrect 3", "Incorrect 4", "Correct"],
            correct_answer="Correct",
            mark=10,
        )
        self.numerical_range_question = NumericalRangeQuestion.objects.create(
            quiz=self.quiz,
            question_text="Test question",
            min_value=1,
            max_value=10,
            mark=10,
        )
        self.guest = GuestAccess.objects.create(
            session_id="Guest abcdefgh"
        )
        self.student_participant = RoomParticipant.objects.create(
            user=self.student,
            room=self.room
        )
        self.guest_participant = RoomParticipant.objects.create(
            guest_access=self.guest,
            room=self.room
        )

    async def test_connection(self):
        communicator = WebsocketCommunicator(
            TutorQuizConsumer.as_asgi(),
            "/ws/live_quiz/ABCD1234/"
        )
        communicator.scope['user'] = self.tutor
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_student_receive(self):
        communicator = WebsocketCommunicator(
            TutorQuizConsumer.as_asgi(),
            "/ws/live_quiz/ABCD1234/"
        )
        communicator.scope['user'] = self.student
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}

        await communicator.connect()

        await communicator.send_json_to({
            "action": "start_quiz"
        })

        response = None
        while True:
            response = await communicator.receive_json_from()
            if response.get("error") == "Only tutors can perform this action.":
                break

        self.assertEqual(response["error"], "Only tutors can perform this action.")

        await communicator.disconnect()

    async def test_receive_start_quiz(self):
        communicator = WebsocketCommunicator(
            TutorQuizConsumer.as_asgi(),
            "/ws/live_quiz/ABCD1234/"
        )
        communicator.scope['user'] = self.tutor
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}

        await communicator.connect()

        await communicator.send_json_to({
            "action": "start_quiz"
        })

        response = None
        while True:
            response = await communicator.receive_json_from()
            if response.get("type") == "quiz_update":
                break

        self.assertEqual(response["type"], "quiz_update")

        await communicator.disconnect()

    async def test_receive_start_empty_quiz(self):
        communicator = WebsocketCommunicator(
            TutorQuizConsumer.as_asgi(),
            "/ws/live_quiz/4321DCBA/"
        )
        communicator.scope['user'] = self.tutor
        communicator.scope['url_route'] = {'kwargs': {'join_code': '4321DCBA'}}

        await communicator.connect()

        await communicator.send_json_to({
            "action": "start_quiz"
        })

        response = None
        while True:
            response = await communicator.receive_json_from()
            if response.get("error") == "No question available":
                break

        self.assertEqual(response["error"], "No question available")

        await communicator.disconnect()

    async def test_receive_end_question(self):
        communicator = WebsocketCommunicator(
            TutorQuizConsumer.as_asgi(),
            "/ws/live_quiz/ABCD1234/"
        )
        communicator.scope['user'] = self.tutor
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}

        await communicator.connect()

        await communicator.send_json_to({
            "action": "end_question"
        })

        response = None
        while True:
            response = await communicator.receive_json_from()
            if response.get("type") == "quiz_update":
                break

        self.assertEqual(response["type"], "quiz_update")

        await communicator.disconnect()

    async def test_receive_end_question_with_no_question(self):
        communicator = WebsocketCommunicator(
            TutorQuizConsumer.as_asgi(),
            "/ws/live_quiz/4321DCBA/"
        )
        communicator.scope['user'] = self.tutor
        communicator.scope['url_route'] = {'kwargs': {'join_code': '4321DCBA'}}

        await communicator.connect()

        await communicator.send_json_to({
            "action": "end_question"
        })

        response = None
        while True:
            response = await communicator.receive_json_from()
            if response.get("error") == "No question to end":
                break

        self.assertEqual(response["error"], "No question to end")

        await communicator.disconnect()

    async def test_receive_next_question_with_no_questions(self):
        communicator = WebsocketCommunicator(
            TutorQuizConsumer.as_asgi(),
            "/ws/live_quiz/ABCD1234/"
        )
        communicator.scope['user'] = self.tutor
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}

        await communicator.connect()

        for i in range(0, 7):
            await communicator.send_json_to({
                "action": "next_question"
            })

        response = None
        while True:
            response = await communicator.receive_json_from()
            if response.get("type") == "quiz_ended":
                break

        self.assertEqual(response["type"], "quiz_ended")

        await communicator.disconnect()

    async def test_receive_next_question_with_more_questions(self):
        question = await database_sync_to_async(IntegerInputQuestion.objects.create)(
            quiz=self.quiz,
            question_text="Test question 2",
            correct_answer=10,
            mark=4,
        )

        communicator = WebsocketCommunicator(
            TutorQuizConsumer.as_asgi(),
            "/ws/live_quiz/ABCD1234/"
        )
        communicator.scope['user'] = self.tutor
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}

        await communicator.connect()

        await communicator.send_json_to({
            "action": "next_question"
        })

        response = None
        while True:
            response = await communicator.receive_json_from()
            if response.get("type") == "quiz_update":
                break

        self.assertEqual(response["type"], "quiz_update")

        await communicator.disconnect()

    async def test_receive_end_quiz(self):
        communicator = WebsocketCommunicator(
            TutorQuizConsumer.as_asgi(),
            "/ws/live_quiz/ABCD1234/"
        )
        communicator.scope['user'] = self.tutor
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}

        await communicator.connect()

        await communicator.send_json_to({
            "action": "end_quiz"
        })

        response = None
        while True:
            response = await communicator.receive_json_from()
            if response.get("type") == "quiz_ended":
                break

        self.assertEqual(response["type"], "quiz_ended")

        await communicator.disconnect()

    async def test_receive_show_stats(self):
        communicator = WebsocketCommunicator(
            TutorQuizConsumer.as_asgi(),
            "/ws/live_quiz/ABCD1234/"
        )
        communicator.scope['user'] = self.tutor
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}

        await communicator.connect()

        await communicator.send_json_to({
            "action": "show_stats"
        })

        response = None
        while True:
            response = await communicator.receive_json_from()
            if response.get("type") == "show_stats":
                break

        self.assertEqual(response["type"], "show_stats")

        await communicator.disconnect()

    async def test_invalid_receive(self):
        communicator = WebsocketCommunicator(
            TutorQuizConsumer.as_asgi(),
            "/ws/live_quiz/ABCD1234/"
        )
        communicator.scope['user'] = self.tutor
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}

        await communicator.connect()

        await communicator.send_json_to({
            "action": "Invalid action"
        })

        response = None
        while True:
            response = await communicator.receive_json_from()
            if response.get("error") == "Unknown action":
                break

        self.assertEqual(response["error"], "Unknown action")

        await communicator.disconnect()
