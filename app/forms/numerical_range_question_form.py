from django import forms
from app.models.quiz import NumericalRangeQuestion

class NumericalRangeQuestionForm(forms.ModelForm):
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

    class Meta:
        model = NumericalRangeQuestion
        fields = ['time', 'question_text', 'mark', 'min_value', 'max_value', 'image']
        widgets = {
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question text'}),
            'min_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter minimum value'}),
            'max_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter maximum value'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        min_value = cleaned_data.get('min_value')
        max_value = cleaned_data.get('max_value')
        if min_value is not None and max_value is not None:
            if min_value > max_value:
                self.add_error('min_value', "Minimum value cannot be greater than maximum value.")
                self.add_error('max_value', "Maximum value must be greater than or equal to the minimum value.")
        return cleaned_data
