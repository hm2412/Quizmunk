from django import forms
from django.contrib.auth.forms import UserCreationForm
from quizsite.app.models import User
from django_password_eye.fields import PasswordEye

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email_address', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['email_address'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your email'})
        self.fields['role'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Select your role'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
        
class LoginForm(forms.Form):
    email_address = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        label="Email Address",
        max_length=255
    )
    password = PasswordEye(label= '')
