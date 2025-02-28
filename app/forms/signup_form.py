from django import forms
from django.contrib.auth.forms import UserCreationForm
from app.models import User

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email_address', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for fieldname in ['first_name', 'last_name', 'email_address', 'role', 'password1', 'password2']:
            self.fields[fieldname].widget.attrs.update({'class': 'form-control', 'placeholder': fieldname,})
