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

    def test_unauthenticated_user_redirect(self):
        """Unauthenticated users should be redirected to the homepage when accessing profile pages."""
        response = self.client.get(reverse("student_profile"))
        self.assertRedirects(response, reverse("homepage"))

        response = self.client.get(reverse("tutor_profile"))
        self.assertRedirects(response, reverse("homepage"))

    def test_student_can_access_student_profile(self):
        """Students should be able to access their own profile page."""
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("student_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student/student_profile.html")

    def test_tutor_can_access_tutor_profile(self):
        """Tutors should be able to access their own profile page."""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("tutor_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tutor/tutor_profile.html")

    def test_student_cannot_access_tutor_profile(self):
        """Students should be forbidden from accessing the tutor profile page."""
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("tutor_profile"))
        self.assertEqual(response.status_code, 403)  # Forbidden access

    def test_tutor_cannot_access_student_profile(self):
        """Tutors should be forbidden from accessing the student profile page."""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("student_profile"))
        self.assertEqual(response.status_code, 403)  # Forbidden access
