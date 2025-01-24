from django import forms
from django.contrib.auth.forms import UserCreationForm
from quizsite.user.models import User

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email_address', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email_address'].widget.attrs.update({'placeholder': 'Enter your email'})
        self.fields['role'].widget.attrs.update({'placeholder': 'Select your role'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter your password', 'class' : 'form-control'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm your password', 'class' : 'form-control'})

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