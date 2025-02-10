from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models.quiz import Quiz, IntegerInputQuestion

User = get_user_model()

class ViewTests(TestCase):
    def setUp(self):
        # Create a student user
        self.student_user = User.objects.create_user(
            first_name="Stu",
            last_name="Dent",
            email_address="student@example.com",
            password="password123",
            role=User.STUDENT,
        )
        # Create a tutor user
        self.tutor_user = User.objects.create_user(
            first_name="Tu",
            last_name = "Tor",
            email_address="tutor@example.com",
            password="password123",
            role=User.TUTOR,
        )
        # Create a quiz
        self.quiz = Quiz.objects.create(
            id="12345678",
            name="My Quiz",
            type="Live",
            tutor=self.tutor_user,
        )
        # Create a question
        self.question = IntegerInputQuestion.objects.create(
            question_text="What is 2+2?",
            correct_answer=4,
            quiz=self.quiz,
        )

    def test_tutor_can_access_create_quiz(self):
        """Tutors should be able to access the create quiz page"""
        self.client.login(email_address="tutor@example.org", password="password123")
        response = self.client.get(reverse("create_quiz"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("tutor/create_quiz.html")

    def test_student_cannot_access_create_quiz(self):
        """Students should not be able to access the create quiz page"""
        self.client.login(email_address="student@example.org", password="password123")
        response = self.client.get(reverse("create_quiz"))
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cannot_access_create_quiz(self):
        """Unauthenticated users should not be able to access the create quiz page"""
        response = self.client.get(reverse("create_quiz"))
        self.assertEqual(response.status_code, 403)

    def test_tutor_can_access_get_question(self):
        """Tutors should be able to access the create quiz page"""
        self.client.login(email_address="tutor@example.org", password="password123")
        response = self.client.get(reverse("get_question", args=["12345678"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("tutor/create_quiz.html")

    def test_student_cannot_access_get_question(self):
        """Students should not be able to access the create quiz page"""
        self.client.login(email_address="student@example.org", password="password123")
        response = self.client.get(reverse("get_question", args=["12345678"]))
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cannot_access_get_question(self):
        """Unauthenticated users should not be able to access the get question page"""
        response = self.client.get(reverse("get_question", args=["12345678"]))
        self.assertEqual(response.status_code, 403)

    #def test_tutor_can_access_edit_quiz_view(self):
    #   """Tutors should be able to access the edit quiz page"""
    #   self.client.login(email_address="tutor@example.org", password="password123")
    #   response = self.client.get(reverse("edit_quiz", args=["12345678"]))
    #   self.assertEqual(response.status_code, 200)
    #   self.assertTemplateUsed("tutor/edit_quiz.html")