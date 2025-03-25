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

    def test_student_dashboard_access(self):
        # Log in as a student
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("student_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student/student_dashboard.html")

    def test_student_cannot_access_tutor_dashboard(self):
        # Log in as a student
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("tutor_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_tutor_dashboard_access(self):
        # Log in as a tutor
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("tutor_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tutor/tutor_dashboard.html")

    def test_tutor_cannot_access_student_dashboard(self):
        # Log in as a tutor
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("student_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_redirect(self):
        # Unauthenticated user tries to access student dashboard
        response = self.client.get(reverse("student_dashboard"))
        self.assertRedirects(response, reverse("homepage"))

        # Unauthenticated user tries to access tutor dashboard
        response = self.client.get(reverse("tutor_dashboard"))
        self.assertRedirects(response, reverse("homepage"))
