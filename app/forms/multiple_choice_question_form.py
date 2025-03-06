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

    class Meta:
        model = MultipleChoiceQuestion
        fields = ['time', 'question_text', 'mark', 'options', 'correct_option', 'image']
        widgets = {
            'time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the time'}),
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question text'}),
            'mark': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the mark'}),
            'correct_option': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the correct option'}),
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

    def clean_options(self):
        options = self.cleaned_data.get('options')
        options_list = [option.strip() for option in options.splitlines() if option.strip()]
        if len(options_list) < 2:
            raise forms.ValidationError("Please enter at least two options.")
        return options_list
    
    def clean(self):
        cleaned_data = super().clean()
        options_list = cleaned_data.get('options')
        correct_option = cleaned_data.get('correct_option')
        if options_list and correct_option:
            if correct_option.strip() not in options_list:
                self.add_error('correct_option', 'the answer should match one of the options')
        return cleaned_data