from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from app.models import User, Room, RoomParticipant, GuestAccess
from app.models.quiz import Quiz

class RoomTestCase(TestCase):
    def setUp(self):
        test_tutor = User.objects.create_user(email_address='tutor@example.com', first_name='Test', last_name='Tutor', role=User.TUTOR)
        test_quiz = Quiz.objects.create(name="Some Quiz", tutor=test_tutor, subject="Computer Science", difficulty="M", type="L")
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
        with self.assertRaises(IntegrityError):
            self.participant = RoomParticipant.objects.create(room=self.room)

    def test_user_and_guest_participant_is_invalid(self):
        with self.assertRaises(IntegrityError):
            self.participant = RoomParticipant.objects.create(room=self.room, user=self.test_user, guest_access=self.guest)

