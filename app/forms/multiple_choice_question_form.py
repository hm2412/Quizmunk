from django import forms
from django.utils.safestring import mark_safe
from app.models.quiz import MultipleChoiceQuestion

class MultipleChoiceOptionsWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ["", ""]
        elif isinstance(value, str):
            value = value.splitlines()

        html = '<div id="multiple-choice-options-container">'
        for option in value:
            html += (
                '<div class="option-input">'
                f'<input type="text" name="{name}[]" value="{option}" class="form-control" placeholder="Enter option" />'
                '</div>'
            )
        html += '</div>'
        
        html += '''
            <div style="display: flex; gap: 8px; margin-top: 10px;">
                <button type="button" id="add-multi-option" class="btn btn-primary" style="width: 40px;">+</button>
                <button type="button" id="remove-multi-option" class="btn btn-danger" style="width: 40px;">-</button>
            </div>
            '''

        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        return data.getlist(name + '[]')

class MultipleChoiceQuestionForm(forms.ModelForm):
    options = forms.CharField(
        help_text="Use the + button to add options, and the - button to remove them",
        widget=MultipleChoiceOptionsWidget(),
    )

    class Meta:
        model = MultipleChoiceQuestion
        fields = ['time', 'question_text', 'mark', 'options', 'correct_answer', 'image']
        widgets = {
            'time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the time'}),
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question text'}),
            'mark': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the mark'}),
            'correct_answer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the correct option'}),
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
        if not isinstance(options, list):
            options = eval(options)
        
        options_list = [option.strip() for option in options if option.strip()]

        print("Cleaned options:", options_list)  # Debug output

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