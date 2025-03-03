from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models import classroom

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
    
    def test_unauthenticated_user_redirects(self):
        # Unauthenticated user tries to access student classrooms
        response = self.client.get(reverse("student_classroom_view"))
        self.assertRedirects(response, reverse("login"))

        # Unauthenticated user tries to access tutor classrooms
        response = self.client.get(reverse("tutor_classroom_view"))
        self.assertRedirects(response, reverse("login"))