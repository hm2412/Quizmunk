from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.core.exceptions import ValidationError
from app.models import User, Quiz, IntegerInputQuestion, TrueFalseQuestion

class QuizTestCase(TestCase):
    def setUp(self):
        self.test_tutor = User.objects.create_user(
            email_address='tutor@example.com', 
            first_name='Test', 
            last_name='Tutor', 
            role=User.TUTOR
        )

        self.quiz = Quiz.objects.create(
            name="Test Quiz",
            subject="Computer Science", 
            difficulty="M",
            type="L",
            is_public=False,
            tutor=self.test_tutor
        )

    def test_valid_quiz_is_valid(self):
        self.assertEqual(self.quiz.name, "Test Quiz")
        self.assertEqual(self.quiz.tutor, self.test_tutor)
        self.assertFalse(self.quiz.is_public)

    def test_quiz_name_max_length(self):
        with self.assertRaises(ValidationError):
            invalid_quiz = Quiz(
                name='A' * 51,
                subject="Test",
                difficulty="M",
                type="L",
                tutor=self.test_tutor
            )
            invalid_quiz.full_clean()

    def test_quiz_subject_max_length(self):
        with self.assertRaises(ValidationError):
            invalid_quiz = Quiz(
                name="Test Quiz",
                subject='A' * 51,
                difficulty="M",
                type="L",
                tutor=self.test_tutor
            )
            invalid_quiz.full_clean()

    def test_quiz_difficulty_choices(self):
        with self.assertRaises(ValidationError):
            invalid_quiz = Quiz(
                name="Test Quiz",
                difficulty="X",
                type="L",
                tutor=self.test_tutor
            )
            invalid_quiz.full_clean()

    def test_quiz_type_choices(self):
        with self.assertRaises(ValidationError):
            invalid_quiz = Quiz(
                name="Test Quiz",
                type="X",
                difficulty="M",
                tutor=self.test_tutor
            )
            invalid_quiz.full_clean()

    def test_tutor_role_constraint(self):
        non_tutor = User.objects.create_user(
            email_address='student@example.com', 
            first_name='Test', 
            last_name='Student', 
            role=User.STUDENT
        )
        
        with self.assertRaises(ValidationError):
            invalid_quiz = Quiz(
                name="Invalid Quiz",
                difficulty="M",
                type="L",
                tutor=non_tutor
            )
            invalid_quiz.full_clean()

    def test_quiz_public_default_value(self):
        quiz = Quiz.objects.create(
            name="Default Quiz",
            subject="Test",
            difficulty="M",
            type="L",
            tutor=self.test_tutor
        )
        self.assertFalse(quiz.is_public)

#Following 3 tests written with assistance from generative AI

    @patch("django.core.files.storage.default_storage.delete")
    def test_save_deletes_old_image_on_update(self, mock_delete):
        image_file = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        question = IntegerInputQuestion.objects.create(
            quiz=self.quiz,
            question_text="What is 2 + 2?",
            mark=5,
            correct_answer=4,
            image=image_file
        )
        old_image_name = question.image.name
        new_image_file = SimpleUploadedFile("new_image.jpg", b"new_content", content_type="image/jpeg")
        question.image = new_image_file
        question.save()
        mock_delete.assert_called_once_with(old_image_name)

    @patch("django.core.files.storage.default_storage.delete")
    def test_delete_deletes_image(self, mock_delete):
        image_file = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        question = IntegerInputQuestion.objects.create(
            quiz=self.quiz,
            question_text="What is 2 + 2?",
            mark=5,
            correct_answer=4,
            image=image_file
        )
        old_image_name = question.image.name
        question.delete()
        mock_delete.assert_called_once_with(old_image_name)

    @patch("django.core.files.storage.default_storage.exists")
    @patch("django.core.files.storage.default_storage.delete")
    def test_delete_does_not_fail_when_image_is_missing(self, mock_delete, mock_exists):
        question = IntegerInputQuestion.objects.create(
            quiz=self.quiz,
            question_text="What is 2 + 2?",
            mark=5,
            correct_answer=4,
        )
        mock_exists.return_value = False
        question.delete()
        mock_delete.assert_not_called()

class QuestionTestCase(TestCase):
    def setUp(self):
        self.test_tutor = User.objects.create_user(
            email_address='tutor@example.com', 
            first_name='Test', 
            last_name='Tutor', 
            role=User.TUTOR
        )

        self.quiz = Quiz.objects.create(
            name="Test Quiz",
            subject="Computer Science", 
            difficulty="M",
            type="L",
            tutor=self.test_tutor
        )

    def test_integer_input_question_creation(self):
        question = IntegerInputQuestion.objects.create(
            quiz=self.quiz,
            question_text="What is 2 + 2?",
            correct_answer=4,
            time=10,
            mark=10
        )
        
        self.assertIsNotNone(question.id)
        self.assertEqual(question.quiz, self.quiz)
        self.assertEqual(question.question_text, "What is 2 + 2?")
        self.assertEqual(question.correct_answer, 4)

    def test_true_false_question_creation(self):
        question = TrueFalseQuestion.objects.create(
            quiz=self.quiz,
            question_text="Is Python a programming language?",
            correct_answer=True,
            time=10,
            mark=10
        )
        
        self.assertIsNotNone(question.id)
        self.assertEqual(question.quiz, self.quiz)
        self.assertEqual(question.question_text, "Is Python a programming language?")
        self.assertTrue(question.correct_answer)

    def test_question_time_choices(self):
        try:
            question = IntegerInputQuestion.objects.create(
                quiz=self.quiz,
                question_text="Test",
                correct_answer=0,
                time=10,  
                mark=10,
                position=1
            )
        except ValidationError:
            self.fail("Unexpected validation error for valid input")
    
    def test_question_mark_choices(self):
        try:
            TrueFalseQuestion.objects.create(
                quiz=self.quiz,
                question_text="Test",
                correct_answer=True,
                time=10,
                mark=10,
                position=1
            )
        except ValidationError:
            self.fail("Unexpected validation error")
