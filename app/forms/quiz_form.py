from django import forms
from app.models import Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['name', 'subject', 'difficulty','quiz_img']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter quiz name'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject'}),
            'difficulty': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter difficulty level'}),
            'type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter type'}),
        }

    def __init__(self, *args, **kwargs):
        super(QuizForm, self).__init__(*args,**kwargs)
        self.fields['quiz_img'].required = False
        
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
