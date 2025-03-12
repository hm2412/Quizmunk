from django import forms
from app.models.quiz import MultipleChoiceQuestion

class MultipleChoiceQuestionForm(forms.ModelForm):
    options = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter one option per line'
        }),
        help_text="Enter at least two options, one per line."
    )

    time = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the time'}),
        error_messages={'invalid': "Time must be an integer."}
    )

    mark = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the mark'}),
        error_messages={'invalid': "Mark must be an integer."}
    )

    correct_answer = forms.CharField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter correct answer'}),
        error_messages={'invalid': "Correct option must be a string."}
    )

    class Meta:
        model = MultipleChoiceQuestion
        fields = ['time', 'question_text', 'mark', 'options', 'correct_answer', 'image']
        widgets = {
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question text'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_options(self):
        options = self.cleaned_data.get('options')
        options_list = [option.strip() for option in options.splitlines() if option.strip()]
        if len(options_list) < 2:
            raise forms.ValidationError("Please enter at least two options.")
        return options_list
    
    def clean(self):
        cleaned_data = super().clean()
        options_list = cleaned_data.get('options')
        correct_answer = cleaned_data.get('correct_answer')
        if options_list and correct_answer:
            if correct_answer.strip() not in options_list:
                self.add_error('correct_answer', 'the answer should match one of the options')
        return cleaned_data