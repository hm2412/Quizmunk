from django import forms
from app.models.quiz import SortingQuestion

class SortingQuestionForm(forms.ModelForm):
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
        model = SortingQuestion
        fields = ['time', 'question_text', 'mark', 'items', 'correct_order', 'image']
        widgets = {
            'time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the time'}),
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question text'}),
            'mark': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the mark'}),
            'items': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter items, separated by commas'}),
            'correct_order': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter correct order, separated by commas'}),
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

    def clean_items(self):
        items = self.cleaned_data.get('items')
        if not items:
            raise forms.ValidationError("Items field cannot be empty.")
        return items

    def clean_correct_order(self):
        correct_order = self.cleaned_data.get('correct_order')
        try:
            order_list = [int(x.strip()) for x in correct_order.split(',')]
        except ValueError:
            raise forms.ValidationError("Correct order must be a comma-separated list of answers.")
        return correct_order
