from django import forms
from django.contrib.auth.forms import UserCreationForm
from app.models import User
from app.models import Quiz, IntegerInputQuestion, TrueFalseQuestion
from django_password_eye.fields import PasswordEye

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email_address', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for fieldname in ['first_name', 'last_name', 'email_address', 'role', 'password1', 'password2']:
            self.fields[fieldname].widget.attrs.update({'class': 'form-control', 'placeholder': fieldname,})
    
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

class QuizForm(forms.ModelForm):
    class Meta:
        model= Quiz
        fields= ['name','subject','difficulty']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter quiz name'}),
            'subject':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject'}),
            'difficulty': forms.Select(attrs={'class': 'form-control','placeholder':'Enter difficulty level'}),
            'type': forms.Select(attrs={'class': 'form-control','placeholder':'Enter type'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Quiz name cannot be empty.")
        return name
    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if not subject:
            raise forms.ValidationError("Subject cannot be empty.")
        return subject
        
        
class IntegerInputQuestionForm(forms.ModelForm):
    class Meta:
        model = IntegerInputQuestion
        fields = ['time','question_text', 'mark', 'correct_answer']
        widgets = {
            'time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the time'}),
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question text'}),
            'mark': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the mark'}),
            'correct_answer':forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter correct answer'}),
        }
    def clean_correct_answer(self):
        correct_answer = self.cleaned_data.get('correct_answer')
        if not isinstance(correct_answer, int):
            raise forms.ValidationError("Correct answer must be an integer.")
        return correct_answer
    
class TrueFalseQuestionForm(forms.ModelForm):
    class Meta:
        model = TrueFalseQuestion
        fields = ['time', 'question_text', 'is_correct', 'mark']
        widgets = {
            'time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the time'}),
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question text'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mark': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the mark'}),
        }