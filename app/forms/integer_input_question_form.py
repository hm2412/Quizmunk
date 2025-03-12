from django import forms
from app.models import IntegerInputQuestion

class IntegerInputQuestionForm(forms.ModelForm): 
    time = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the time'}),
        error_messages={'invalid': "Time must be an integer."}
    )

    mark = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the mark'}),
        error_messages={'invalid': "Mark must be an integer."}
    )

    correct_answer = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter correct answer'}),
        error_messages={'invalid': "Correct answer must be an integer."}
    )

    class Meta:
        model = IntegerInputQuestion
        fields = ['time', 'question_text', 'mark', 'correct_answer', 'image']
        widgets = {
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question text'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_correct_answer(self):
        return self.cleaned_data.get('correct_answer')
