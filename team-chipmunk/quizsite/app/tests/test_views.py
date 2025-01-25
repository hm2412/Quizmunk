from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class ViewTests(TestCase):
    def setUp(self):
        # Create a student user
        self.student_user = User.objects.create_user(
            email_address="student@example.com",
            password="password123",
            role=User.STUDENT,
        )
        # Create a tutor user
        self.tutor_user = User.objects.create_user(
            email_address="tutor@example.com",
            password="password123",
            role=User.TUTOR,
        )

    def test_student_dashboard_access(self):
        # Log in as a student
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("student_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_dashboard.html")

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
        self.assertTemplateUsed(response, "tutor_dashboard.html")

    def test_tutor_cannot_access_student_dashboard(self):
        # Log in as a tutor
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("student_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_homepage_redirects_logged_in_student(self):
        # Log in as a student
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("homepage"))
        self.assertRedirects(response, reverse("student_dashboard"))

    def test_homepage_redirects_logged_in_tutor(self):
        # Log in as a tutor
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("homepage"))
        self.assertRedirects(response, reverse("tutor_dashboard"))

    def test_unauthenticated_user_redirect(self):
        # Unauthenticated user tries to access student dashboard
        response = self.client.get(reverse("student_dashboard"))
        self.assertRedirects(response, reverse("homepage"))

        # Unauthenticated user tries to access tutor dashboard
        response = self.client.get(reverse("tutor_dashboard"))
        self.assertRedirects(response, reverse("homepage"))

    def test_login_redirects_authenticated_users(self):
        # Log in as a student
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("student_dashboard"))

        # Log in as a tutor
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("tutor_dashboard"))

    def test_signup_redirects_authenticated_users(self):
        # Log in as a student
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("sign_up"))
        self.assertRedirects(response, reverse("student_dashboard"))

        # Log in as a tutor
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("sign_up"))
        self.assertRedirects(response, reverse("tutor_dashboard"))
