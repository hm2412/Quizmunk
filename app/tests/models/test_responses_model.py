from django.test import TestCase
from django.core.exceptions import ValidationError
from app.models import User, Quiz, TrueFalseQuestion, IntegerInputQuestion, TrueFalseResponse, IntegerInputResponse

class ResponseTestCase(TestCase):
    def setUp(self):
        self.test_tutor = User.objects.create_user(
            email_address='tutor@tutor.com',
            first_name='Test',
            last_name='Tutor',
            role=User.TUTOR
        )

        self.test_player = User.objects.create_user(
            email_address='player@player.com',
            first_name='Test',
            last_name='Player',
            role=User.STUDENT
        )

        self.quiz = Quiz.objects.create(
            name="Test Quiz",
            subject="Computer Science",
            difficulty="M",
            type="L",
            tutor=self.test_tutor
        )

        self.true_false_question = TrueFalseQuestion.objects.create(
            quiz=self.quiz,
            question_text="Is this a true or false question?",
            is_correct=True,
            time=10,
            mark=5
        )

        self.integer_input_question = IntegerInputQuestion.objects.create(
            quiz=self.quiz,
            question_text="What is 2 + 2?",
            correct_answer=4,
            time=10,
            mark=5
        )

    def test_valid_true_false_question_response(self):
        response = TrueFalseResponse.objects.create(
            player=self.test_player,
            question=self.true_false_question,
            answer=True
        )
        try:
            response.full_clean()
        except ValidationError:
            self.fail("ValidationError raised")

    def test_invalid_true_false_question_response(self):
        with self.assertRaises(ValidationError):
            response = TrueFalseResponse.objects.create(
                player=self.test_player,
                question=self.true_false_question,
                answer=7
            )

    def test_valid_integer_question_response(self):
        response = IntegerInputResponse.objects.create(
            player=self.test_player,
            question=self.integer_input_question,
            answer=7
        )
        try:
            response.full_clean()
        except ValidationError:
            self.fail("ValidationError raised")

    def test_invalid_integer_question_response(self):
        with self.assertRaises(ValidationError):
            response = IntegerInputResponse.objects.create(
                player=self.test_player,
                question=self.integer_input_question,
                answer=7.5
            )
