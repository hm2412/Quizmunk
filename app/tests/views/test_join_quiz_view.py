from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

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

    def test_student_can_access_join_quiz(self):
        """Students should be able to access the join quiz page"""
        self.client.login(email_address="student@example.org", password="password123")
        response = self.client.get(reverse("join_quiz"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("join.html")

    def test_unauthenticated_user_can_access_join_quiz(self):
        """Unauthenticated users should be able to access the join quiz page"""
        response = self.client.get(reverse("join_quiz"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("join.html")

    def test_tutors_cannot_access_join_quiz(self):
        """Tutors should not be able to access the join quiz page"""
        self.client.login(email_address="tutor@example.org", password="123")
        response = self.client.get(reverse("join_quiz"))
        self.assertEqual(response.status_code, 403)