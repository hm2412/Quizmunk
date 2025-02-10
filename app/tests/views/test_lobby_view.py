from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models.room import Room

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
        # Create a room
        self.room = Room.objects.create(name="myRoom", join_code="12345678")

    def test_student_can_access_join_quiz(self):
        """Students should be able to access the quiz lobby page"""
        self.client.login(email_address="student@example.org", password="password123")
        response = self.client.get(reverse("lobby", args=["12345678"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("lobby.html")

    def test_unauthenticated_user_can_access_join_quiz(self):
        """Unauthenticated users should be able to access the quiz lobby page"""
        response = self.client.get(reverse("lobby", args=["12345678"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("lobby.html")

    def test_tutors_can_access_join_quiz(self):
        """Tutors should be able to access quiz lobby page"""
        self.client.login(email_address="tutor@example.org", password="123")
        response = self.client.get(reverse("lobby", args=["12345678"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("lobby.html")