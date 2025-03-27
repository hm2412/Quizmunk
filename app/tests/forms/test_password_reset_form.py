from django import forms
from django.test import TestCase
from django.contrib.auth import get_user_model
from app.forms import PasswordResetForm

class PasswordResetFormTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email_address="testuser@example.org",
            password="TestPassword123",
            first_name="Test",
            last_name="User",
            role="student"
        )

        self.form_input = {
            'old_password': 'TestPassword123',
            'new_password': 'NewPassword123',
            'confirm_password': 'NewPassword123'
        }

    # currently fails
    def test_valid_password_reset_form(self):
        form = PasswordResetForm(data=self.form_input, user=self.user)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = PasswordResetForm(user=self.user)
        self.assertIn('old_password', form.fields)
        self.assertIn('new_password', form.fields)
        self.assertIn('confirm_password', form.fields)

        old_password_field = form.fields['old_password']
        self.assertTrue(isinstance(old_password_field.widget, forms.PasswordInput))

        new_password_field = form.fields['new_password']
        self.assertTrue(isinstance(new_password_field.widget, forms.PasswordInput))

        confirm_password_field = form.fields['confirm_password']
        self.assertTrue(isinstance(confirm_password_field.widget, forms.PasswordInput))

    def test_old_password_is_required(self):
        self.form_input['old_password'] = ''
        form = PasswordResetForm(data=self.form_input, user=self.user)
        self.assertFalse(form.is_valid())

    def test_new_password_is_required(self):
        self.form_input['new_password'] = ''
        form = PasswordResetForm(data=self.form_input, user=self.user)
        self.assertFalse(form.is_valid())

    def test_confirm_password_is_required(self):
        self.form_input['confirm_password'] = ''
        form = PasswordResetForm(data=self.form_input, user=self.user)
        self.assertFalse(form.is_valid())

    def test_old_password_is_incorrect(self):
        self.form_input['old_password'] = 'NotOldPassword'
        form = PasswordResetForm(data=self.form_input, user=self.user)
        self.assertFalse(form.is_valid())

    def test_new_password_and_confirm_password_are_identical(self):
        self.form_input['confirm_password'] = 'DiffPassword123'
        form = PasswordResetForm(data=self.form_input, user=self.user)
        self.assertFalse(form.is_valid())

    def test_new_password_fails_strong_validation(self):
        self.form_input['new_password'] = '123'
        self.form_input['confirm_password'] = '123'
        form = PasswordResetForm(data=self.form_input, user=self.user)
        self.assertFalse(form.is_valid())
