from django import forms
from app.models.quiz import TrueFalseQuestion

class TrueFalseQuestionForm(forms.ModelForm):
    time = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'min': '0', 'class': 'form-control', 'placeholder': 'Enter the time'}),
        error_messages={'invalid': "Time must be an integer."}
    )

    mark = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'min': '0', 'class': 'form-control', 'placeholder': 'Enter the mark'}),
        error_messages={'invalid': "Mark must be an integer."}
    )
    
    correct_answer = forms.TypedChoiceField(
        choices=((True, 'True'), (False, 'False')),
        coerce=lambda x: x == 'True',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True,
        label='Correct Answer'
    )

    class Meta:
        model = TrueFalseQuestion
        fields = ['time', 'question_text', 'correct_answer', 'mark', 'image']
        widgets = {
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question text'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
    
    def clean_correct_answer(self):
        return self.cleaned_data.get('correct_answer')
