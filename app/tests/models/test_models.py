from django.test import TestCase
from django.core.exceptions import ValidationError
from app.models.quiz import Quiz

class QuizTestCase(TestCase):
    def setUp(self):
        ID = "0123456789"
        name = "Some Quiz"
        tutorID = "9876543210"
        subject = "Computer Science"
        difficulty = "M"
        type = "L"
        self.quiz = Quiz.objects.create(quizID=ID, name=name, tutorID=tutorID, subject=subject, difficulty=difficulty, type=type)

    def test_valid_quiz_is_valid(self):
        try:
            self.quiz.full_clean()
        except ValidationError:
            self.fail("Default test quiz should be deemed valid")

    def test_quiz_with_no_quizID_is_invalid(self):
        self.quiz.quizID=""
        with self.assertRaises(ValidationError):
            self.quiz.full_clean()

    def test_quiz_with_overlong_quizID_is_invalid(self):
        self.quiz.quizID="1" * 256
        with self.assertRaises(ValidationError):
            self.quiz.full_clean()

    def test_quiz_with_no_name_is_invalid(self):
        self.quiz.name=""
        with self.assertRaises(ValidationError):
            self.quiz.full_clean()

    def test_quiz_with_overlong_name_is_invalid(self):
        self.quiz.name="1" * 256
        with self.assertRaises(ValidationError):
            self.quiz.full_clean()

    def test_quiz_with_no_tutorID_is_invalid(self):
        self.quiz.tutorID=""
        with self.assertRaises(ValidationError):
            self.quiz.full_clean()

    def test_quiz_with_overlong_tutorID_is_invalid(self):
        self.quiz.tutorID="1" * 256
        with self.assertRaises(ValidationError):
            self.quiz.full_clean()

    def test_quiz_with_no_type_is_invalid(self):
        self.quiz.type=""
        with self.assertRaises(ValidationError):
            self.quiz.full_clean()

    def test_quiz_with_overlong_type_is_invalid(self):
        self.quiz.type="L" * 256
        with self.assertRaises(ValidationError):
            self.quiz.full_clean()

    def test_quiz_with_no_subject_is_valid(self):
        self.quiz.subject=""
        try:
            self.quiz.full_clean()
        except ValidationError:
            self.fail("Default test quiz should be deemed valid")

    def test_quiz_with_overlong_subject_is_invalid(self):
        self.quiz.subject="L" * 256
        with self.assertRaises(ValidationError):
            self.quiz.full_clean()

    def test_quiz_with_no_difficulty_is_valid(self):
        self.quiz.difficulty=""
        try:
            self.quiz.full_clean()
        except ValidationError:
            self.fail("Default test quiz should be deemed valid")

    def test_quiz_with_overlong_difficulty_is_invalid(self):
        self.quiz.difficulty="L" * 256
        with self.assertRaises(ValidationError):
            self.quiz.full_clean()