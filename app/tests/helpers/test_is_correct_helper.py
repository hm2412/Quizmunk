from decimal import Decimal
from django.test import TestCase
from app.helpers.helper_functions import isCorrectAnswer
from app.models import User, TrueFalseQuestion, IntegerInputQuestion, NumericalRangeQuestion, TrueFalseResponse, Quiz, \
    Room, NumericalRangeResponse

class TestIsCorrectHelper(TestCase):
    def setUp(self):
        # Creating a test user (a tutor)
        self.tutor = User.objects.create_user(
            email_address='tutor@example.com',
            first_name='Tutor',
            last_name='User',
            role=User.TUTOR
        )

        # Create a quiz linked to the tutor
        self.quiz = Quiz.objects.create(
            name="Sample Quiz",
            subject="General Knowledge",
            difficulty="E",  # Easy
            type="L",  # Live
            tutor=self.tutor
        )

        self.room = Room.objects.create(
            name="Sample Room",
            quiz=self.quiz
        )

        # Create questions for the quiz
        self.tf_question = TrueFalseQuestion.objects.create(
            question_text='Is this a true/false question?',
            correct_answer=True,
            quiz=self.quiz,
            position=1,
            time=30,
            mark=1
        )

        self.int_question = IntegerInputQuestion.objects.create(
            question_text='What is 2+2?',
            correct_answer=4,
            quiz=self.quiz,
            position=2,
            time=30,
            mark=1
        )

        self.num_range_question = NumericalRangeQuestion.objects.create(
            question_text='Pick a number between 10 and 20.',
            min_value=10.0,
            max_value=20.0,
            quiz=self.quiz,
            position=3,
            time=30,
            mark=1
        )

        self.player = User.objects.create_user(
            email_address='fake@email.com',
            first_name='Fake',
            last_name='User',
            role = User.STUDENT
        )

    def test_tf_correct_response(self):
        self.tf_response = TrueFalseResponse.objects.create(question=self.tf_question, answer=True, player=self.player, room=self.room)
        self.assertTrue(isCorrectAnswer(self.tf_response))
        self.assertTrue(self.tf_response.correct)

    def test_num_range_correct_response(self):
        self.num_range_response = NumericalRangeResponse.objects.create(question=self.num_range_question, answer=13, player=self.player, room=self.room)
        self.assertTrue(isCorrectAnswer(self.num_range_response))
        self.assertTrue(self.num_range_response.correct)

    def test_num_range_incorrect_response(self):
        self.num_range_response = NumericalRangeResponse.objects.create(question=self.num_range_question, answer=55, player=self.player, room=self.room)
        self.assertFalse(isCorrectAnswer(self.num_range_response))
