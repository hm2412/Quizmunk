from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models.stats import Stats, QuestionStats
from app.models.room import RoomParticipant, Room, GuestAccess
from app.models.quiz import Quiz, Question, TrueFalseQuestion
from app.models.classroom import Classroom
import datetime
from django.contrib.contenttypes.models import ContentType
from unittest.mock import patch, MagicMock
from app.models.responses import TrueFalseResponse

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

        self.question = TrueFalseQuestion.objects.create(question_text="do you breathe air?",quiz=self.quiz, mark=5,correct_answer=True)
        # Create a Room for the quiz
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
        self.csv_download_player_url = reverse('stats_download_player', args=[self.stats.id])
        self.csv_download_question_url = reverse('stats_download_question', args=[self.stats.id])

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
        self.participant = RoomParticipant.objects.create(
            user=self.student_user,
            room=self.room,
            joined_at=datetime.datetime.now(),
            score=85
        )

        guest = GuestAccess.objects.create(session_id="guest123456789")
        RoomParticipant.objects.create(
            guest_access=guest,
            user=None,
            room=self.room,
            joined_at=datetime.datetime.now(),
            score=70
        )
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(self.csv_download_player_url)

        content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Participant", content)
        self.assertIn("student@example.com", content)  # student participant
        self.assertIn("Guest (guest123)", content)    # guest participant
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("player_stats_", response["Content-Disposition"])

    def test_csv_download_student_forbidden(self):
        """Ensure students cannot download the quiz stats CSV."""
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(self.csv_download_player_url)
        self.assertEqual(response.status_code, 403)  # Should be forbidden
   
    def test_csv_download_question(self):
        """Ensure question CSV download works and includes correct headers."""

        self.question.question_text = "Do you breathe air?"
        self.question.save()
        
        # Create a participant
        participant = RoomParticipant.objects.create(
            user=self.student_user,
            room=self.room,
            score=100,
            joined_at=datetime.datetime.now()
        )
        # 3 correct
        for _ in range(3):
            TrueFalseResponse.objects.create(
                player=self.student_user,
                room=self.room,
                question=self.question,
                answer=True,
                correct=True
            )
        # 1 incorrect
        TrueFalseResponse.objects.create(
            player=self.student_user,
            room=self.room,
            question=self.question,
            answer=False,
            correct=False
        )
        # Create QuestionStats (triggers save)
        QuestionStats.objects.create(
            room=self.room,
            question=self.question,
            question_type=ContentType.objects.get_for_model(self.question),
            question_id=self.question.id
        )

        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(self.csv_download_question_url)
        content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("Question,Total Responses,Correct Responses", content)
        self.assertIn("75.00%", content)
        self.assertIn("Do you breathe air?", content)

    def test_player_responses_view(self):
        """Test player_responses view using real data."""
        # Create participant (student) and response
        participant = RoomParticipant.objects.create(
            user=self.student_user,
            room=self.room,
            score=90,
            joined_at=datetime.datetime.now()
        )

        # Create a real response
        TrueFalseResponse.objects.create(
            player=self.student_user,
            room=self.room,
            question=self.question,
            answer=True,
            correct=True
        )
        TrueFalseResponse.objects.create(
            player=self.student_user,
            room=self.room,
            question=self.question,
            answer=False,
            correct=False
        )

        self.client.login(email_address="tutor@example.com", password="password123")
        url = reverse('player_responses', args=[self.room.id, participant.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/player_responses.html')
        self.assertEqual(response.context['correct_count'], 1)
        self.assertEqual(response.context['incorrect_count'], 1)

    def test_guest_responses_view(self):
        """Test player_responses view using real data ie guest."""
        guest = GuestAccess.objects.create(session_id="guest123456789")
        participant = RoomParticipant.objects.create(
            guest_access=guest,
            room=self.room,
            score=60,
            joined_at=datetime.datetime.now()
        )

        # Create a real response
        TrueFalseResponse.objects.create(
            guest_access=guest,
            room=self.room,
            question=self.question,
            answer=True,
            correct=True
        )
        TrueFalseResponse.objects.create(
            guest_access=guest,
            room=self.room,
            question=self.question,
            answer=False,
            correct=False
        )

        self.client.login(email_address="tutor@example.com", password="password123")
        url = reverse('player_responses', args=[self.room.id, participant.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/player_responses.html')
        self.assertEqual(response.context['correct_count'], 1)
        self.assertEqual(response.context['incorrect_count'], 1)
        self.assertIn("Guest (guest123)", response.context['player'])
    def test_question_responses_view(self):
        """Test question_responses."""
        # Attach the question to the room
        self.room.get_questions = lambda: [self.question]

        # Create responses
        TrueFalseResponse.objects.create(
            player=self.student_user,
            room=self.room,
            question=self.question,
            answer=True,
            correct=True
        )
        TrueFalseResponse.objects.create(
            player=self.student_user,
            room=self.room,
            question=self.question,
            answer=False,
            correct=False
        )

        self.client.login(email_address="tutor@example.com", password="password123")
        url = reverse('question_responses', args=[self.room.id, self.question.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/question_responses.html')
        self.assertEqual(response.context['correct_count'], 1)
        self.assertEqual(response.context['incorrect_count'], 1)

    def test_student_stats_view(self):
        """Test student stats view with actual quiz history."""
        participant = RoomParticipant.objects.create(
            user=self.student_user,
            room=self.room,
            score=85,
            joined_at=datetime.datetime.now()
        )

        # Add a correct response
        TrueFalseResponse.objects.create(
            player=self.student_user,
            room=self.room,
            question=self.question,
            answer=True,
            correct=True
        )

        self.client.login(email_address="student@example.com", password="password123")
        url = reverse('student_stats', args=[self.student_user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/student_stats.html')
        self.assertGreaterEqual(response.context['average_score'], 0)
        self.assertIn('best_score', response.context)

    def test_classroom_stats_view(self):
        """Test classroom stats with real Stats and Room setup."""
        self.classroom = Classroom.objects.create(name="Test Class", tutor=self.tutor_user,description="i love school")
        self.room.classroom = self.classroom
        self.room.save()

        self.client.login(email_address="tutor@example.com", password="password123")
        url = reverse('classroom_stats_view', args=[self.classroom.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/classroom_stats.html')
        self.assertIn(self.stats, response.context['stats_list'])

    def test_question_responses_404_when_question_not_in_room(self):
        """Test question_responses raises 404 if question is not part of room quiz."""

        # Create a second question that's NOT part of the room (simulate mismatch)
        other_quiz = Quiz.objects.create(
            name="Another Quiz",
            subject="Science",
            difficulty="E",
            type="L",
            tutor=self.tutor_user
        )
        other_question = TrueFalseQuestion.objects.create(
            question_text="Is water wet?",
            quiz=other_quiz,
            mark=5,
            correct_answer=True
        )

        # Override room.get_questions() to return only the original question
        self.room.get_questions = lambda: [self.question]

        self.client.login(email_address="tutor@example.com", password="password123")
        url = reverse('question_responses', args=[self.room.id, other_question.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

