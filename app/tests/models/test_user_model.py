from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from app.models import User

class RoomTestCase(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(email_address='user@example.com', first_name='Test', last_name='User', role=User.STUDENT)

    def test_default_user_is_valid(self):
        try:
            self.test_user.full_clean()
        except ValidationError:
            self.fail('Default user should be valid')


    def test_tutor_user_is_valid(self):
        self.test_user.role = User.TUTOR
        try:
            self.test_user.full_clean()
        except ValidationError:
            self.fail('Default tutor should be valid')

    def test_overlong_first_name_is_invalid(self):
        self.test_user.first_name = 'This name needs to be over 50 characters long so I will keep typing'
        with self.assertRaises(ValidationError):
            self.test_user.full_clean()

    def test_overlong_last_name_is_invalid(self):
        self.test_user.last_name = 'This name needs to be over 50 characters long so I will keep typing'
        with self.assertRaises(ValidationError):
            self.test_user.full_clean()

    def test_invalid_email_address_is_invalid(self):
        self.test_user.email_address = 'Invalid email address'
        with self.assertRaises(ValidationError):
            self.test_user.full_clean()

    def test_empty_email_address_is_invalid(self):
        self.test_user.email_address = ''
        with self.assertRaises(ValidationError):
            self.test_user.full_clean()

    def test_empty_first_name_is_invalid(self):
        self.test_user.first_name = ''
        with self.assertRaises(ValidationError):
            self.test_user.full_clean()

    def test_empty_last_name_is_invalid(self):
        self.test_user.last_name = ''
        with self.assertRaises(ValidationError):
            self.test_user.full_clean()

    def test_create_duplicate_email_invalid(self):
        with self.assertRaises(IntegrityError):
            self.test_user2 = User.objects.create_user(email_address='user@example.com', first_name='Test2', last_name='User2', role=User.STUDENT)

    def test_create_duplicate_name_valid(self):
        try:
            self.test_user2 = User.objects.create_user(email_address='user2@example.com', first_name='Test', last_name='User', role=User.STUDENT)
        except IntegrityError:
            self.fail('Duplicate Email Addresses should be valid')

