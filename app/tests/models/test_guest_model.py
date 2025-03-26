from django.test import TestCase
from django.core.exceptions import ValidationError
import uuid

from app.models import GuestAccess

class GuestTestCase(TestCase):
    def setUp(self):
        self.valid_session_id = str(uuid.uuid4())
        self.guest = GuestAccess.objects.create(classroom_code="ABC123", session_id=self.valid_session_id)

    def test_guest_access_creation(self):
        self.assertIsNotNone(self.guest.id)
        self.assertEqual(self.guest.classroom_code, "ABC123")
        self.assertEqual(self.guest.session_id, self.valid_session_id)

    def test_auto_generate_session_id(self):
        guest = GuestAccess.objects.create(classroom_code="XYZ789")
        self.assertIsNotNone(guest.session_id)
        self.assertEqual(len(guest.session_id), 36)

    def test_classroom_code_validation(self):
        guest = GuestAccess(classroom_code="Invalid!@£", session_id=str(uuid.uuid4()))
        with self.assertRaises(ValidationError):
            guest.full_clean()

    def test_unique_session_id_constraint(self):
        duplicate_guest = GuestAccess(classroom_code="ROOM2", session_id=self.valid_session_id)
        with self.assertRaises(Exception):
            duplicate_guest.save()

    def test_str_method(self):
        self.assertEqual(str(self.guest), "Guest - Classroom Code: ABC123")

    def test_blank_classroom_code_raises_error(self):
        guest = GuestAccess(classroom_code="", session_id=str(uuid.uuid4()))
        with self.assertRaises(ValidationError):
            guest.full_clean()

    def test_generated_session_id_length(self):
        guest = GuestAccess(classroom_code="TestRoom")
        guest.save()
        self.assertEqual(len(guest.session_id), 36)

    def test_classroom_code_case_sensitive(self):
        guest1 = GuestAccess.objects.create(classroom_code="ROOM", session_id=str(uuid.uuid4()))
        guest2 = GuestAccess.objects.create(classroom_code="room", session_id=str(uuid.uuid4()))
        self.assertNotEqual(guest1.classroom_code, guest2.classroom_code)

    def test_duplicate_classroom_code_allowed(self):
        GuestAccess.objects.create(classroom_code="SAME", session_id=str(uuid.uuid4()))
        try:
            GuestAccess.objects.create(classroom_code="SAME", session_id=str(uuid.uuid4()))
        except Exception:
            self.fail("Duplicate classroom_code should be allowed.")

    def test_classroom_code_with_spaces_or_symbols_invalid(self):
        invalid_codes = ["abc 123", "code!", "room@#", "test_code"]
        for code in invalid_codes:
            guest = GuestAccess(classroom_code=code, session_id=str(uuid.uuid4()))
            with self.assertRaises(ValidationError):
                guest.full_clean()
