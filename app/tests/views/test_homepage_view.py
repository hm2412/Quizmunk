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

    def test_about_us(self):
        # Test that the About Us page renders and uses the correct template
        response = self.client.get(reverse("about_us"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about.html")

    def test_never_cache(self):
        # Test that browser doesn't cache any responses
        response = self.client.get(reverse("homepage"))
        self.assertIn('Cache-Control', response)
        self.assertIn('no-cache', response['Cache-Control'])

    def test_homepage_for_anonymous_user(self):
        # Test that the homepage renders correctly for guests
        response = self.client.get(reverse("homepage"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")