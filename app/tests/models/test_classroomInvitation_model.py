from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from app.models.classroom import Classroom, ClassroomInvitation
from app.models.user import User

class ClassroomInvitationTestCase(TestCase):
    def setUp(self):
        self.tutor = User.objects.create_user(email_address='tutor@example.com', first_name='Tutor', last_name='User', role=User.TUTOR)
        self.student = User.objects.create_user(email_address='student@example.com', first_name='Student', last_name='User', role=User.STUDENT)
        self.classroom = Classroom.objects.create(name="Testing Class", tutor=self.tutor)
        self.invite = ClassroomInvitation.objects.create(classroom=self.classroom, student=self.student, status='pending')

    def test_valid_invite_is_valid(self):
        try:
            self.invite.full_clean()
        except ValidationError:
            self.fail("Valid ClassroomInvitation should be deemed valid")

    def test_duplicate_invite_is_invalid(self):
        with self.assertRaises(IntegrityError):
            ClassroomInvitation.objects.create(classroom=self.classroom, student=self.student, status='pending')

    def test_classroomless_invite_is_invalid(self):
        with self.assertRaises(IntegrityError):
            ClassroomInvitation.objects.create(classroom=None, student=self.student, status='pending')

    def test_studentless_invite_is_invalid(self):
        with self.assertRaises(IntegrityError):
            ClassroomInvitation.objects.create(classroom=self.classroom, student=None, status='pending')

    def test_invalid_status_value_is_invalid(self):
        self.invite.status = "not_a_valid_status"
        with self.assertRaises(ValidationError):
            self.invite.full_clean()

    def test_status_choices_are_valid(self):
        valid_statuses = ['pending', 'accepted', 'declined']
        for status in valid_statuses:
            self.invite.status = status
            try:
                self.invite.full_clean()
            except ValidationError:
                self.fail(f"Status '{status}' should be valid")
