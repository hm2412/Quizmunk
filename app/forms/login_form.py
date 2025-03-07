from django import forms
from django_password_eye.fields import PasswordEye

class LoginForm(forms.Form):
    email_address = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        label="Email Address",
        max_length=255,
        error_messages={'required': 'Please enter your email address.'}
    )
    password = PasswordEye(
        label= '',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        error_messages={'required': 'Please enter your password.'}
    )
