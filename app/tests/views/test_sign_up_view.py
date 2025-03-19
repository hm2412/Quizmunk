from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.forms import SignUpForm

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

    def test_signup_redirects_authenticated_users(self):
        # Log in as a student
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("sign_up"))
        self.assertRedirects(response, reverse("student_dashboard"))

        # Log in as a tutor
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("sign_up"))
        self.assertRedirects(response, reverse("tutor_dashboard"))


class SignUpViewTest(TestCase):
    def setUp(self):
        self.signup_url = reverse('sign_up')

    def test_get_sign_up_view(self):
        """Test GET request returns the sign-up page."""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        self.assertIsInstance(response.context['form'], SignUpForm)

    def test_post_valid_sign_up(self):
        """Test POST request with valid data fully covers user creation and login."""
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email_address': 'test@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'role': User.TUTOR, 
        }
        response = self.client.post(self.signup_url, data, follow=True)
        self.assertTrue(User.objects.filter(email_address='test@example.com').exists())
        user = User.objects.get(email_address='test@example.com')
        self.assertTrue(user.is_authenticated)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(response, reverse('tutor_dashboard'))

    def test_post_invalid_sign_up(self):
        """Test POST request with invalid form (password mismatch)."""
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email_address': 'test@example.com',  # Use email_address or email
            'password1': 'SecurePass123!',
            'password2': 'WrongPass123!',
            'role': User.TUTOR, 
        }
        response = self.client.post(self.signup_url, data)

        # Ensure the user is not created
        self.assertFalse(User.objects.filter(email_address='test@example.com').exists())

        # Ensure the user is not logged in
        self.assertNotIn('_auth_user_id', self.client.session)

        # Ensure form returns validation error
        self.assertContains(response, "The two password fields didn’t match.", html=True)