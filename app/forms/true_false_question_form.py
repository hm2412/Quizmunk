from django import forms
from app.models.quiz import TrueFalseQuestion

class TrueFalseQuestionForm(forms.ModelForm):
    time = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the time'}),
        error_messages={'invalid': "Time must be an integer."}
    )

    mark = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the mark'}),
        error_messages={'invalid': "Mark must be an integer."}
    )

    is_correct = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False  # Optional, prevents errors if not checked
    )

    class Meta:
        model = TrueFalseQuestion
        fields = ['time', 'question_text', 'is_correct', 'mark', 'image']
        widgets = {
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question text'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
