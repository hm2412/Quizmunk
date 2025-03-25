from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from app.models import User

class UserTestCase(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(email_address='user@example.com', first_name='Test', last_name='User', role=User.STUDENT)

    def test_create_user_without_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email_address='',
                first_name='Test',
                last_name='User'
            )

    def test_create_user_without_first_name(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email_address='test@example.com',
                first_name='',
                last_name='User'
            )

    def test_create_user_without_last_name(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email_address='test@example.com',
                first_name='Test',
                last_name=''
            )

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email_address='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='password123'
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_superuser_not_staff(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email_address='admin@example.com',
                first_name='Admin',
                last_name='User',
                is_staff=False
            )

    def test_create_superuser_not_superuser(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email_address='admin@example.com',
                first_name='Admin',
                last_name='User',
                is_superuser=False
            )

    def test_get_by_natural_key(self):
        user = User.objects.get_by_natural_key('user@example.com')
        self.assertEqual(user, self.test_user)

    def test_str_method(self):
        self.assertEqual(str(self.test_user), 'user@example.com')

    def test_user_is_active_by_default(self):
        self.assertTrue(self.test_user.is_active)

    def test_user_is_not_staff_by_default(self):
        self.assertFalse(self.test_user.is_staff)

    def test_student_is_default_role(self):
        new_user = User.objects.create_user(
            email_address='new@example.com',
            first_name='New',
            last_name='User'
        )
        self.assertEqual(new_user.role, User.STUDENT)

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
            User.objects.create_user(
                email_address='user@example.com',
                first_name='Test2',
                last_name='User2',
                role=User.STUDENT
            )

    def test_create_duplicate_name_valid(self):
        try:
            User.objects.create_user(
                email_address='user2@example.com',
                first_name='Test',
                last_name='User',
                role=User.STUDENT
            )
        except IntegrityError:
            self.fail('Duplicate names should be valid')

    def test_create_user_with_normalized_email(self):
        user = User.objects.create_user(
            email_address='TEST@EXAMPLE.COM',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.email_address, 'TEST@example.com')

    def test_create_superuser_with_password(self):
        superuser = User.objects.create_superuser(
            email_address='admin2@example.com',
            first_name='Admin',
            last_name='User',
            password='testpass123'
        )
        self.assertTrue(superuser.check_password('testpass123'))

    def test_create_user_with_normalized_email(self):
        user = User.objects.create_user(
            email_address='TEST@EXAMPLE.COM',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.email_address, 'TEST@example.com')

    def test_invalid_role_choice(self):
        self.test_user.role = 'invalid_role'
        with self.assertRaises(ValidationError):
            self.test_user.full_clean()

    def test_user_ordering(self):
        User.objects.create_user(
            email_address='a@example.com',
            first_name='A',
            last_name='User'
        )
        User.objects.create_user(
            email_address='b@example.com',
            first_name='B',
            last_name='User'
        )
        users = User.objects.all()
        self.assertEqual(users[0].email_address, 'a@example.com')
        self.assertEqual(users[1].email_address, 'b@example.com')
        self.assertEqual(users[2].email_address, 'user@example.com')

    def test_required_fields(self):
        self.assertEqual(User.REQUIRED_FIELDS, ['first_name', 'last_name'])
        self.assertEqual(User.USERNAME_FIELD, 'email_address')
