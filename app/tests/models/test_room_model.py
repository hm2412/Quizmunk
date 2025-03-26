from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction

from app.models import User, Room, RoomParticipant, GuestAccess, IntegerInputQuestion, TrueFalseQuestion
from app.models.quiz import Quiz

class RoomTestCase(TestCase):
    def setUp(self):
        test_tutor = User.objects.create_user(email_address='tutor@example.com', first_name='Test', last_name='Tutor', role=User.TUTOR)
        test_quiz = Quiz.objects.create(name="Some Quiz", tutor=test_tutor, subject="Computer Science", difficulty="M", type="L")
        IntegerInputQuestion.objects.create(
            quiz = test_quiz,
            question_text = f"The answer to this sample question is {60}",
            correct_answer = 60,
            time = 60,
            mark = 1,
            position=1
        )

        TrueFalseQuestion.objects.create(
            quiz = test_quiz,
            question_text = f"The answer to this sample question is {str(60 % 2 == 0)}",
            correct_answer = (60 % 2 == 0),
            time = 60,
            mark = 1,
            position=2,
        )
        
        self.test_user = User.objects.create_user(email_address='user@example.com', first_name='Test', last_name='User', role=User.STUDENT)
        self.guest = GuestAccess.objects.create(classroom_code='TestClassroom')
        self.room = Room.objects.create(name="Test Room", quiz=test_quiz)

    def test_valid_room_is_valid(self):
        try:
            self.room.full_clean()
        except ValidationError:
            self.fail("Default test room should be deemed valid")

    def test_blank_room_name_is_invalid(self):
        self.room.name = ""
        with self.assertRaises(ValidationError):
            self.room.full_clean()

    def test_overlong_room_name_is_invalid(self):
        self.room.name = "This is a room name that needs to be over 50 characters long so I will make it over 50 characters long"
        with self.assertRaises(ValidationError):
            self.room.full_clean()

    def test_blank_quiz_is_valid(self):
        self.room.quiz = None
        try:
            self.room.full_clean()
        except ValidationError:
            self.fail("Empty quiz should be deemed valid")

    def test_default_room_participant_is_valid(self):
        self.participant = RoomParticipant.objects.create(room=self.room, user=self.test_user)
        try:
            self.participant.full_clean()
        except ValidationError:
            self.fail("Default participant should be deemed valid")

    def test_default_guest_participant_is_valid(self):
        self.participant = RoomParticipant.objects.create(room=self.room, guest_access=self.guest)
        try:
            self.participant.full_clean()
        except ValidationError:
            self.fail("Default guest participant should be deemed valid")

    def test_roomless_participant_is_invalid(self):
        with self.assertRaises(IntegrityError):
            self.participant = RoomParticipant.objects.create(room=None, user=self.test_user)

    def test_userless_participant_is_invalid(self):
        with transaction.atomic():
            participant = RoomParticipant(room=self.room)
            with self.assertRaises(ValidationError):
                participant.clean()
            transaction.set_rollback(True)

    def test_user_and_guest_participant_is_invalid(self):
        with transaction.atomic():
            participant = RoomParticipant(room=self.room, user=self.test_user, guest_access=self.guest)
            with self.assertRaises(ValidationError):
                participant.clean()
            transaction.set_rollback(True)

    def test_get_questions(self):
        questions = self.room.get_questions()
        self.assertTrue(isinstance(questions, list))
        self.assertTrue(all(q.quiz == self.room.quiz for q in questions))
    
    def test_get_questions_no_quiz(self):
        self.room.quiz = None
        self.assertListEqual([], self.room.get_questions())
    
    def test_get_current_question_valid_index(self):
        questions = self.room.get_questions()
        current_question = self.room.get_current_question()
        self.assertEqual(current_question, questions[self.room.current_question_index])

    def test_get_current_question_negative_index(self):
        original_index = self.room.current_question_index
        self.room.current_question_index = -1
        current_question = self.room.get_current_question()
        self.assertIsNone(current_question)
        self.room.get_current_question = original_index

    def test_get_current_question_out_of_bounds_index(self):
        original_index = self.room.current_question_index
        question_count = len(self.room.get_questions())
        self.room.current_question_index = question_count
        current_question = self.room.get_current_question()
        self.assertIsNone(current_question)
        self.room.current_question_index = original_index

    def test_get_next_question(self):
        next_position = self.room.current_question_index + 2

        next_question = self.room.next_question()
        self.assertEqual(next_question.position, next_position)

    def test_room_str(self):
        self.assertEqual(str(self.room), f"Room: {self.room.name} (Code: {self.room.join_code})")

    def test_str_user(self):
        participant = RoomParticipant(room=self.room, user=self.test_user)
        self.assertEqual(str(participant), f"User: {self.test_user.email_address}")

    def test_str_guest(self):
        participant = RoomParticipant(room=self.room, guest_access=self.guest)
        self.assertEqual(str(participant), f"Guest: {self.guest.session_id[:8]}")
