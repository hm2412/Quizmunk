from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

User = get_user_model()

class PasswordResetViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email_address="student@example.com",
            password="oldpassword123",
            first_name="Test",
            last_name="Student",
            role="student"
        )
        self.url = reverse("password_reset")  # Adjust if your URL name is different

    def test_login_required_redirects(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_get_form_authenticated(self):
        self.client.login(email_address="student@example.com", password="oldpassword123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Update Password")

    def test_successful_password_reset(self):
        self.client.login(email_address="student@example.com", password="oldpassword123")
        response = self.client.post(self.url, {
            "old_password": "oldpassword123",
            "new_password": "newsecurepass456",
            "confirm_password": "newsecurepass456"
        }, follow=True)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newsecurepass456"))
        expected_redirect = reverse("student_dashboard") if self.user.role == "student" else reverse("tutor_dashboard")
        self.assertRedirects(response, expected_redirect)


        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("successfully changed" in str(m) for m in messages))

    def test_incorrect_old_password(self):
        self.client.login(email_address="student@example.com", password="oldpassword123")
        response = self.client.post(self.url, {
            "old_password": "wrongpassword",
            "new_password": "newsecurepass456",
            "confirm_password": "newsecurepass456"
        })

        self.assertContains(response, "Incorrect current password.")

    def test_mismatched_new_passwords(self):
        self.client.login(email_address="student@example.com", password="oldpassword123")
        response = self.client.post(self.url, {
            "old_password": "oldpassword123",
            "new_password": "pass1",
            "confirm_password": "pass2"
        })

        self.assertContains(response, "Passwords do not match.")

    def test_password_too_short(self):
        self.client.login(email_address="student@example.com", password="oldpassword123")
        response = self.client.post(self.url, {
            "old_password": "oldpassword123",
            "new_password": "123",
            "confirm_password": "123"
        })

        self.assertContains(response, "This password is too short")
