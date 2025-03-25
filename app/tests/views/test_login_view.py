from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.forms import LoginForm

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

    def test_login_view_get(self):
    # GET request should render the correct template, and include the login form.
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertIsInstance(response.context['form'], LoginForm)

    def test_login_redirects_authenticated_users(self):
        # Log in as a student
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("student_dashboard"))

        # Log in as a tutor
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("tutor_dashboard"))

    def test_invalid_login_email(self):
        # Invalid credentials lead back to the login page
        data = {
            'email_address': 'nonexistent@example.com',
            'password': 'password123'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email or password")

    def test_invalid_login_password(self):
        # Invalid credentials lead back to the login page
        data = {
            'email_address': 'student@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email or password")

    def test_logout_view(self):
        # Test that logouts work
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("student_dashboard"))

        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

        response = self.client.get(reverse("login"))
        self.assertContains(response, "Logged out successfully!")

    def test_never_cache(self):
        # Test that browser doesn't cache any responses
        response = self.client.get(reverse('login'))
        self.assertIn('Cache-Control', response)
        self.assertIn('no-cache', response['Cache-Control'])