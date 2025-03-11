from django.db import IntegrityError
from django.test import TestCase
from app.models import Room, RoomParticipant, User, GuestAccess, Quiz, Stats, IntegerInputQuestion, TrueFalseQuestion, \
    TextInputQuestion


class StatsModelTests(TestCase):

    def setUp(self): #setUp assisted with generative AI
        self.tutor = User.objects.create_user(
            email_address="tutor@example.com",
            first_name="John",
            last_name="Doe",
            password="password123",
            role=User.TUTOR
        )

        # Create a quiz instance
        self.quiz = Quiz.objects.create(
            name="Test Quiz",
            subject="General Knowledge",
            difficulty="M",
            type="L",
            tutor=self.tutor  # Assign the tutor user
        )

        # Create questions for the quiz

        # Integer Input Question
        int_question = IntegerInputQuestion.objects.create(
            question_text="What is 2 + 2?",
            position=1,
            time=30,
            quiz=self.quiz,
            mark=1,
            correct_answer=4
        )

        # True/False Question
        true_false_question = TrueFalseQuestion.objects.create(
            question_text="Is the Earth flat?",
            position=2,
            time=30,
            quiz=self.quiz,
            mark=1,
            correct_answer=False
        )

        # Text Input Question
        text_question = TextInputQuestion.objects.create(
            question_text="What is the capital of France?",
            position=3,
            time=30,
            quiz=self.quiz,
            mark=1,
            correct_answer="Paris"
        )


        # Create a room instance with the quiz attached
        self.room = Room.objects.create(name="Test Room", quiz=self.quiz)

        # Create users for room participants
        self.user1 = User.objects.create_user(
            email_address="user1@example.com",
            first_name="John",
            last_name="Doe",
            password="password123"
        )
        self.user2 = User.objects.create_user(
            email_address="user2@example.com",
            first_name="Jane",
            last_name="Doe",
            password="password123"
        )
        self.user3 = User.objects.create_user(
            email_address="user3@example.com",
            first_name="Jim",
            last_name="Beam",
            password="password123"
        )

    def test_valid_stats(self):
        self.participant1 = RoomParticipant.objects.create(room=self.room, user=self.user1, score=80)
        self.participant2 = RoomParticipant.objects.create(room=self.room, user=self.user2, score=90)
        self.participant3 = RoomParticipant.objects.create(room=self.room, user=self.user3, score=70)
        try:
            self.stats = Stats.objects.create(
                room=self.room,
                quiz=self.quiz
            )
        except IntegrityError:
            self.fail("Stats creation failed")
        self.assertEqual(self.stats.mean_score, 80)
        self.assertEqual(self.stats.median_score, 80)

    def test_empty_room_stats(self):
        try:
            self.stats = Stats.objects.create(
                room=self.room,
                quiz=self.quiz
            )
        except IntegrityError:
            self.fail("Stats creation failed")

