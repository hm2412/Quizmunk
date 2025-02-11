from django.test import TestCase
from app.forms import LoginForm
from django import forms

class LoginFormTestCase(TestCase):
    def setUp(self):
        self.form_input = {
            'email_address': 'test@example.com',
            'password': 'Password123'
        }

    def test_valid_login_form(self):
        form = LoginForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = LoginForm()
        self.assertIn('email_address', form.fields)
        self.assertIn('password', form.fields)
        email_field = form.fields['email_address']
        password_field = form.fields['password']
        self.assertTrue(isinstance(email_field.widget, forms.EmailInput))
        self.assertTrue(isinstance(password_field.widget, forms.PasswordInput))

    def test_form_refuses_invalid_email(self):
        self.form_input['email_address'] = 'invalid_email'
        form = LoginForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_valid_email(self):
        self.form_input['email_address'] = 'valid@example.com'
        form = LoginForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_email_length_validation(self):
        self.form_input['email_address'] = 'a' * 250 + '@example.com'
        form = LoginForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_not_be_empty(self):
        self.form_input['password'] = ''
        form = LoginForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['password'],
            ['Please enter your password.']
        )

    def test_email_must_not_be_empty(self):
        self.form_input['email_address'] = ''
        form = LoginForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['email_address'],
            ['Please enter your email address.']
        )