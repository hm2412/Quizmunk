from django.contrib.auth.hashers import check_password
from django import forms
from django.test import TestCase
from app.forms import SignUpForm
from app.models import User

class SignUpFormTestCase(TestCase):
    def setUp(self):
        self.form_input = {
            'first_name': 'Test',
            'last_name': 'McStudent',
            'email_address': 'teststudent@example.org',
            'role':'student',
            'password1': 'TestPassword11',
            'password2': 'TestPassword11'
        }

    def test_valid_sign_up_form(self):
        form = SignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = SignUpForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('email_address', form.fields)
        email_field = form.fields['email_address']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('password1', form.fields)
        new_password_widget = form.fields['password1'].widget
        self.assertTrue(isinstance(new_password_widget, forms.PasswordInput))
        self.assertIn('password2', form.fields)
        password_confirmation_widget = form.fields['password2'].widget
        self.assertTrue(isinstance(password_confirmation_widget, forms.PasswordInput))
        self.assertIn('role', form.fields)
        role_field = form.fields['role']
        self.assertTrue(isinstance(role_field.widget, forms.Select))

    def test_first_name_is_required(self):
        self.form_input['first_name'] = ''
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_last_name_is_required(self):
        self.form_input['last_name'] = ''
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_email_is_required(self):
        self.form_input['email_address'] = ''
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_role_is_required(self):
        self.form_input['role'] = ''
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_is_not_name(self):
        self.form_input['password1'] = 'McStudent'
        self.form_input['password2'] = 'McStudent'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_length(self):
        self.form_input['password1'] = 'pword'
        self.form_input['password2'] = 'pword'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_letter(self):
        self.form_input['password1'] = '123456789'
        self.form_input['password2'] = '123456789'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_not_be_common(self):
        self.form_input['password1'] = 'Password123'
        self.form_input['password2'] = 'Password123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password2'] = 'WrongPassword123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = SignUpForm(data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        user = User.objects.get(email_address='teststudent@example.org')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'McStudent')
        self.assertEqual(user.role, 'student')
        is_password_correct = check_password('TestPassword11', user.password)
        self.assertTrue(is_password_correct)
