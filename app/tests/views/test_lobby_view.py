from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from app.models import Classroom, Quiz, ClassroomStudent
from app.models.room import Room, RoomParticipant

User = get_user_model()

class ViewTests(TestCase):
    def setUp(self):
        # Create student users
        self.student_user = User.objects.create_user(
            first_name="Stu",
            last_name="Dent",
            email_address="student@example.com",
            password="password123",
            role=User.STUDENT,
        )
        self.student_user2 = User.objects.create_user(
            first_name="Class",
            last_name="Student",
            email_address="classroom@example.com",
            password="password123",
            role=User.STUDENT
        )
        # Create tutor users
        self.tutor_user1 = User.objects.create_user(
            first_name="Tu",
            last_name = "Tor",
            email_address="tutor@example.com",
            password="password123",
            role=User.TUTOR,
        )
        self.tutor_user2 = User.objects.create_user(
            first_name="Tu",
            last_name = "Tor",
            email_address="tutor2@example.com",
            password="password123",
            role=User.TUTOR,
        )
        # Create a classroom
        self.classroom = Classroom.objects.create(id=1, name="my_classroom", tutor=self.tutor_user1, description="A test classroom")

        # Create a quiz
        self.quiz = Quiz.objects.create(id=1, name="my_quiz", type="L", tutor=self.tutor_user1)

        # Create a room with a classroom
        self.room1 = Room.objects.create(name="myRoom", join_code="12345678", classroom=self.classroom, quiz=self.quiz)

        # Create a room without a classroom
        self.room2 = Room.objects.create(name="myRoom", join_code="87654321", quiz=self.quiz)

        # Create a classroom student
        self.classroom_student = ClassroomStudent.objects.create(classroom=self.classroom, student=self.student_user2)

    def test_student_can_join_other_classroom_lobby(self):
        """Students should be able to access the quiz lobby of a classroom they are in"""
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("lobby", args=["12345678"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("lobby.html")

    def test_student_can_join_their_classroom_lobby(self):
        """Students should be able to access the quiz lobby page of a quiz from a different classroom"""
        self.client.login(email_address="classroom@example.com", password="password123")
        response = self.client.get(reverse("lobby", args=["12345678"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("lobby.html")

    def test_student_can_access_join_lobby_without_a_classroom(self):
        """Students should be able to access the quiz lobby of a quiz with no classroom"""
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("lobby", args=["87654321"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("lobby.html")

    def test_tutors_can_access_lobby_in_a_classroom(self):
        """Tutors should be able to access quiz lobby page"""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("lobby", args=["12345678"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("lobby.html")

    def test_tutors_can_access_lobby_without_a_classroom(self):
        """Tutors should be able to access quiz lobby page"""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("lobby", args=["87654321"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("lobby.html")

    def test_tutors_can_access_lobby_without_a_classroom(self):
        """Tutors should be able to access quiz lobby page"""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("lobby", args=["87654321"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("lobby.html")

    def test_unauthenticated_user_can_access_join_lobby_without_a_classroom(self):
        """Unauthenticated users should be able to access the quiz lobby page"""
        response = self.client.get(reverse("lobby", args=["87654321"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("lobby.html")

    def test_unauthenticated_user_can_access_join_lobby_in_a_classroom(self):
        """Unauthenticated users should be able to access the quiz lobby page"""
        response = self.client.get(reverse("lobby", args=["12345678"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("lobby.html")

    def test_valid_setup_quiz(self):
        """Quiz setup should redirect to lobby page"""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("setup_quiz", args=[self.quiz.id]))

        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed("lobby.html")
        self.assertTrue(Room.objects.filter(quiz=self.quiz).exists())

    def test_invalid_setup_quiz(self):
        """Quiz setup should not redirect if quiz ID is invalid"""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("setup_quiz", args=[1000]))
        self.assertTemplateNotUsed("lobby.html")

    def test_valid_classroom_setup_quiz(self):
        """Classroom quiz setup should redirect to the lobby page after making a room"""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("setup_classroom_quiz", args=[self.quiz.id, self.classroom.id]))

        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed("lobby.html")
        self.assertTrue(Room.objects.filter(quiz=self.quiz, classroom=self.classroom).exists())

    def test_invalid_classroom_classroom_setup_quiz(self):
        """Classroom quiz setup should not load lobby page if quiz ID is invalid"""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("setup_classroom_quiz", args=[self.quiz.id, 1000]))
        self.assertTemplateNotUsed("lobby.html")
