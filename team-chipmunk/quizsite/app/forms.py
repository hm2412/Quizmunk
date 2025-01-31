from django import forms
from django.contrib.auth.forms import UserCreationForm
from quizsite.app.models import User, Quiz, IntegerInputQuestion, TrueFalseQuestion
from django_password_eye.fields import PasswordEye

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email_address', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Choose a username'})
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

class QuizForm(forms.ModelForm):
    class Meta:
        model= Quiz
        fields= ['name','tutorID','subject','difficulty']
        
class IntegerInputQuestionForm(forms.ModelForm):
    class Meta:
        model = IntegerInputQuestion
        fields = ['number', 'time', 'quizID', 'question_text', 'mark', 'correct_answer']

class TrueFalseQuestionForm(forms.ModelForm):
    class Meta:
        model = TrueFalseQuestion
        fields = ['number', 'time', 'quizID', 'question_text', 'is_correct', 'mark']