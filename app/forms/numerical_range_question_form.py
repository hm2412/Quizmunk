from django import forms
from app.models.quiz import NumericalRangeQuestion

class NumericalRangeQuestionForm(forms.ModelForm):
    class Meta:
        model = NumericalRangeQuestion
        fields = ['time', 'question_text', 'mark', 'min_value', 'max_value', 'image']
        widgets = {
            'time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the time'}),
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question text'}),
            'mark': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the mark'}),
            'min_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter minimum value'}),
            'max_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter maximum value'}),
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