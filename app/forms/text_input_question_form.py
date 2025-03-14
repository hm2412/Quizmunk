from django import forms
from app.models.quiz import TextInputQuestion

class TextInputQuestionForm(forms.ModelForm):
    class Meta:
        model = TextInputQuestion
        fields = ['time', 'question_text', 'correct_answer', 'mark', 'image']
        widgets = {
            'time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the time'}),
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question text'}),
            #maybe add a way to make the tutor check that the spilling is correct
            'correct_answer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter correct answer'}),
            'mark': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the mark'}),
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
