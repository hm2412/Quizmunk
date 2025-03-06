from django import forms
from app.models.quiz import DecimalInputQuestion
from decimal import Decimal

class DecimalInputQuestionForm(forms.ModelForm):
    class Meta:
        model = DecimalInputQuestion
        fields = ['time', 'question_text', 'mark', 'correct_answer', 'image']
        widgets = {
            'time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the time'}),
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question text'}),
            'mark': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the mark'}),
            'correct_answer': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter correct answer'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
    
    def clean_time(self):
        time = self.cleaned_data.get('time')
        if not isinstance(time, int):
            raise forms.ValidationError("Time must be an integer.")
        return time

    def clean_mark(self):
        mark = self.cleaned_data.get('mark')
        if not isinstance(mark, int):
            raise forms.ValidationError("Mark must be an integer.")
        return mark

    def clean_correct_answer(self):
        correct_answer = self.cleaned_data.get('correct_answer')
        if not isinstance(correct_answer, Decimal):
            raise forms.ValidationError("Correct answer must be a decimal.")
        return correct_answer
