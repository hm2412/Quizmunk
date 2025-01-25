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
        for fieldname in ['email_address', 'role', 'password1', 'password2']:
            if fieldname in ['password2']:
                self.fields[fieldname].widget.attrs.update({'class': 'form-control', 'placeholder': 'confirm password',})
            self.fields[fieldname].widget.attrs.update({'class': 'form-control', 'placeholder': fieldname,})
        
class LoginForm(forms.Form):
    email_address = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        label="Email Address",
        max_length=255
    )
    password = PasswordEye(label= '')
