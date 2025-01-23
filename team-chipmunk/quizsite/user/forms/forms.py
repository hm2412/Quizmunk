from django import forms
from django.contrib.auth.forms import UserCreationForm
from models.models import User

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email_address', 'role', 'password', 'password_confirmation']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email_address'].widget.attrs.update({'placeholder': 'Enter your email'})
        self.fields['role'].widget.attrs.update({'placeholder': 'Select your role'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Enter your password'})
        self.fields['password_confirmation'].widget.attrs.update({'placeholder': 'Confirm your password'})

class LoginForm(forms.Form):
    email_address = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}),
        label="Email Address",
        max_length=255
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        label="Password"
    )