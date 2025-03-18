from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models.stats import Stats
from app.models.room import RoomParticipant, Room
from app.models.quiz import Quiz

User = get_user_model()


class StatsViewTests(TestCase):
    def setUp(self):
        """Set up test data for stats views"""
        self.client = Client()

        # Create a tutor user
        self.tutor_user = User.objects.create_user(
            first_name="Tu",
            last_name="Tor",
            email_address="tutor@example.com",
            password="password123",
            role=User.TUTOR,
        )

        # Create a student user
        self.student_user = User.objects.create_user(
            first_name="Stu",
            last_name="Dent",
            email_address="student@example.com",
            password="password123",
            role=User.STUDENT,
        )

        # Create a quiz
        self.quiz = Quiz.objects.create(
            name="Python Basics", 
            subject="Programming",
            difficulty="E",  
            type="L",  
            tutor=self.tutor_user
        )

        # ✅ Create a Room for the quiz
        self.room = Room.objects.create(join_code="XYZ123", quiz=self.quiz)

        # Create stats for the quiz
        self.stats = Stats.objects.create(
            quiz=self.quiz, 
            room=self.room,
            date_played="2025-03-11 14:30"
        )
        # URL patterns
        self.stats_url = reverse('stats')
        self.stats_details_url = reverse('stats_details', args=[self.stats.id])
        self.csv_download_url = reverse('stats_download', args=[self.stats.id])

    def test_stats_view_requires_login(self):
        """Ensure non-authenticated users cannot access stats page."""
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login page

    def test_stats_view_tutor_access(self):
        """Ensure tutors can access the stats page and see their quizzes."""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(self.stats_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/stats.html')
        self.assertIn(self.stats, response.context['stats_list'])

    def test_stats_view_student_forbidden(self):
        """Ensure students cannot access tutor stats."""
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, 403)  # Forbidden due to @is_tutor decorator

    def test_stats_details_view(self):
        """Ensure tutors can access detailed quiz stats."""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(self.stats_details_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/stats_detail.html')
        self.assertEqual(response.context['stats'].id, self.stats.id)

    def test_stats_details_access_restriction(self):
        """Ensure students cannot access tutor stats details."""
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(self.stats_details_url)
        self.assertEqual(response.status_code, 403)  # Should be forbidden

    def test_csv_download(self):
        """Ensure CSV download works correctly for tutors."""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(self.csv_download_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("quiz_stats_", response["Content-Disposition"])

    def test_csv_download_student_forbidden(self):
        """Ensure students cannot download the quiz stats CSV."""
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(self.csv_download_url)
        self.assertEqual(response.status_code, 403)  # Should be forbidden
