from django import forms
from app.models.quiz import TextInputQuestion

class TextInputQuestionForm(forms.ModelForm):
    time = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the time'}),
        error_messages={'invalid': "Time must be an integer."}
    )

    mark = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the mark'}),
        error_messages={'invalid': "Mark must be an integer."}
    )

    correct_answer = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter correct answer'}),
        error_messages={'invalid': "Correct answer must be a string."}
    )

    class Meta:
        model = TextInputQuestion
        fields = ['time', 'question_text', 'correct_answer', 'mark', 'image']
        widgets = {
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question text'}),
            #maybe add a way to make the tutor check that the spelling is correct
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_correct_answer(self):
        return self.cleaned_data.get('correct_answer')
