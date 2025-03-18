from django import forms
from app.models.quiz import NumericalRangeQuestion

class NumericalRangeQuestionForm(forms.ModelForm):
    time = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the time'}),
        error_messages={'invalid': "Time must be an integer."}
    )

    mark = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the mark'}),
        error_messages={'invalid': "Mark must be an integer."}
    )

    class Meta:
        model = NumericalRangeQuestion
        fields = ['time', 'question_text', 'mark', 'min_value', 'max_value', 'image']
        widgets = {
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question text'}),
            'min_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter minimum value'}),
            'max_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter maximum value'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }