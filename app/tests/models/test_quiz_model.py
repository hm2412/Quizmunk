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
            tutor=self.test_tutor
        )
        

    def test_valid_quiz_is_valid(self):
        self.assertEqual(self.quiz.name, "Test Quiz")
        self.assertEqual(self.quiz.tutor, self.test_tutor)

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
            is_correct=True,
            time=10,
            mark=10
        )
        
        self.assertIsNotNone(question.id)
        self.assertEqual(question.quiz, self.quiz)
        self.assertEqual(question.question_text, "Is Python a programming language?")
        self.assertTrue(question.is_correct)

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
                is_correct=True,
                time=10,
                mark=10,
                position=1
            )
        except ValidationError:
            self.fail("Unexpected validation error")