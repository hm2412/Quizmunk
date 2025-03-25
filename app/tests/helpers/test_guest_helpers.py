from django.test import TestCase
from app.helpers.helper_functions import get_guest_responses, calculate_guest_score
from app.models import (
    User, Quiz, Room, RoomParticipant,
    GuestAccess, NumericalRangeQuestion, NumericalRangeResponse,
    TrueFalseQuestion, TrueFalseResponse
)

class TestGuestHelpers(TestCase):
    def setUp(self):
        # Create a tutor user
        self.tutor = User.objects.create_user(
            email_address='tutor@example.com',
            first_name='Tutor',
            last_name='User',
            role=User.TUTOR
        )

        # Create a quiz and room
        self.quiz = Quiz.objects.create(
            name="Test Quiz",
            subject="Math",
            difficulty="E",
            type="L",
            tutor=self.tutor
        )

        self.room = Room.objects.create(name="Room 1", quiz=self.quiz)

        # Create a guest user
        self.guest = GuestAccess.objects.create(
            classroom_code="ABC123"
        )

        # Create a numerical range question (marked out of 5)
        self.range_question = NumericalRangeQuestion.objects.create(
            question_text="Pick a number between 1 and 10",
            quiz=self.quiz,
            position=1,
            time=30,
            min_value=1,
            max_value=10,
            mark=5
        )

        # Create a true/false question (marked out of 3)
        self.tf_question = TrueFalseQuestion.objects.create(
            question_text="Is water wet?",
            quiz=self.quiz,
            position=2,
            time=30,
            correct_answer=True,
            mark=3
        )

    def test_get_guest_responses(self):
        # Create correct guest responses
        NumericalRangeResponse.objects.create(
            guest_access=self.guest,
            room=self.room,
            question=self.range_question,
            answer=5
        )

        TrueFalseResponse.objects.create(
            guest_access=self.guest,
            room=self.room,
            question=self.tf_question,
            answer=True
        )

        responses = get_guest_responses(self.guest, self.room)
        self.assertEqual(len(responses), 2)
        self.assertTrue(all(r.correct for r in responses))

    def test_calculate_guest_score(self):
        # Add responses: both are correct
        NumericalRangeResponse.objects.create(
            guest_access=self.guest,
            room=self.room,
            question=self.range_question,
            answer=3  # Correct
        )

        TrueFalseResponse.objects.create(
            guest_access=self.guest,
            room=self.room,
            question=self.tf_question,
            answer=True  # Correct
        )

        score = calculate_guest_score(self.guest, self.room)

        # Expected:
        # Base = 5 + 3 = 8
        # Streak Bonus = 0
        # Speed Bonus: +3 (first), +2 (second)
        # Total: 8 + 3 + 2 = 13

        self.assertEqual(score, 13)

    def test_guest_incorrect_answer(self):
        # Add an incorrect response
        TrueFalseResponse.objects.create(
            guest_access=self.guest,
            room=self.room,
            question=self.tf_question,
            answer=False  # Incorrect
        )

        score = calculate_guest_score(self.guest, self.room)
        self.assertEqual(score, 0)

    def test_guest_score_with_null_guest(self):
        score = calculate_guest_score(None, self.room)
        self.assertEqual(score, 0)

    def test_guest_score_with_null_room(self):
        score = calculate_guest_score(self.guest, None)
        self.assertEqual(score, 0)

    def test_get_guest_responses_with_no_answers(self):
        responses = get_guest_responses(self.guest, self.room)
        self.assertEqual(responses, [])
