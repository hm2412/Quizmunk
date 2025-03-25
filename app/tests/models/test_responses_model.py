from django.test import TestCase
from django.core.exceptions import ValidationError
from app.models import User, Quiz, TrueFalseQuestion, IntegerInputQuestion, TrueFalseResponse, IntegerInputResponse, \
    TextInputQuestion, TextInputResponse, Room, MultipleChoiceQuestion, MultipleChoiceResponse


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

        self.room = Room.objects.create(
            name="Test Room",
            quiz=self.quiz
        )

        self.true_false_question = TrueFalseQuestion.objects.create(
            quiz=self.quiz,
            question_text="Is this a true or false question?",
            correct_answer=True,
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

        self.text_input_question = TextInputQuestion.objects.create(
            quiz=self.quiz,
            question_text="Is the answer to this question yes?",
            correct_answer="Yes",
            time=10,
            mark=5
        )

        self.multiple_choice_question = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            question_text="What is 2 + 2?",
            options=["1", "2", "3", "4"],
            correct_answer="4",
            time=10,
            mark=5
        )


    def test_valid_true_false_question_response(self):
        response = TrueFalseResponse.objects.create(
            player=self.test_player,
            question=self.true_false_question,
            answer=True,
            room=self.room
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
                answer=7,
                room=self.room
            )

    def test_valid_integer_question_response(self):
        response = IntegerInputResponse.objects.create(
            player=self.test_player,
            question=self.integer_input_question,
            answer=7,
            room=self.room
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
                answer=7.5,
                room=self.room
            )

    def test_valid_text_question_response(self):
        response = TextInputResponse.objects.create(
            player=self.test_player,
            question=self.text_input_question,
            answer="Yes",
            room=self.room
        )
        try:
            response.full_clean()
        except ValidationError:
            self.fail("ValidationError raised")

    def test_invalid_text_question_response(self):
        response = TextInputResponse.objects.create(
            player=self.test_player,
            question=self.text_input_question,
            answer=5,
            room=self.room
        )
        try:
            response.full_clean()
        except ValidationError:
            self.fail("ValidationError raised")

    def test_valid_multiple_choice_question_response(self):
        response = MultipleChoiceResponse.objects.create(
            player=self.test_player,
            question=self.multiple_choice_question,
            answer="4",
            room=self.room
        )
        try:
            response.full_clean()
        except ValidationError:
            self.fail("ValidationError raised")

    def test_invalid_multiple_choice_question_response(self):
        with self.assertRaises(ValidationError):
            response = MultipleChoiceResponse.objects.create(
                player=self.test_player,
                question=self.multiple_choice_question,
                answer="5",
                room=self.room
            )

    def test_str_integer_input_response(self):
        response = IntegerInputResponse.objects.create(
            player=self.test_player,
            room=self.room,
            question=self.integer_input_question,
            answer=4,
        )
        self.assertEqual(str(response),
                         f"Integer Input Answer by {self.test_player.email_address} for question {self.integer_input_question}: {response.answer}")

