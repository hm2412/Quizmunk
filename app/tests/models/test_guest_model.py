from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
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
    