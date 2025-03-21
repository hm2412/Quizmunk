from django import forms
from django.utils.safestring import mark_safe
from app.models.quiz import MultipleChoiceQuestion
from ast import literal_eval

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
                <button type="button" id="add-option" class="btn btn-primary" style="width: 40px;">+</button>
                <button type="button" id="remove-option" class="btn btn-danger" style="width: 40px;">-</button>
            </div>
            '''
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        key = name + "[]"
        if hasattr(data, 'getlist'):
            result = data.getlist(key)
            if not result:
                # Fallback: try using the field name.
                result = data.getlist(name)
            return result
        else:
            result = data.get(key)
            if result is None:
                result = data.get(name)
            if result is None:
                return []
            if isinstance(result, list):
                return result
            return [result]

class MultipleChoiceQuestionForm(forms.ModelForm):
    time = forms.IntegerField(
        error_messages={'invalid': "Time must be an integer."},
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the time'})
    )
    mark = forms.IntegerField(
        error_messages={'invalid': "Mark must be an integer."},
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the mark'})
    )
    options = forms.CharField(
        help_text="Use the + button to add options, and the - button to remove them",
        widget=MultipleChoiceOptionsWidget(),
    )

    class Meta:
        model = MultipleChoiceQuestion
        fields = ['time', 'question_text', 'mark', 'options', 'correct_answer', 'image']
        widgets = {
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question text'}),
            'correct_answer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the correct option'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_options(self):
        raw_options = self.cleaned_data.get('options')
        if not raw_options:
            raise forms.ValidationError("This field is required.")
        if isinstance(raw_options, list):
            if len(raw_options) == 1:
                raw_options = raw_options[0]
            else:
                raw_options = "\n".join(raw_options)
        raw_options = raw_options.strip()
        if raw_options.startswith('[') and raw_options.endswith(']'):
            try:
                evaluated = literal_eval(raw_options)
                if (isinstance(evaluated, list) and len(evaluated) == 1 and
                    isinstance(evaluated[0], str) and
                    evaluated[0].strip().startswith('[') and evaluated[0].strip().endswith(']')):
                    evaluated = literal_eval(evaluated[0].strip())
                if isinstance(evaluated, list):
                    options_list = evaluated
                else:
                    options_list = raw_options.splitlines()
            except Exception:
                options_list = raw_options.splitlines()
        else:
            options_list = raw_options.splitlines()
        options_list = [opt.strip() for opt in options_list if opt.strip()]
        if len(options_list) < 2:
            raise forms.ValidationError("Please enter at least two options.")
        return options_list
    
    def clean(self):
        cleaned_data = super().clean()
        options_list = cleaned_data.get('options')
        correct_answer = cleaned_data.get('correct_answer')
        if options_list and correct_answer:
            if correct_answer.strip() not in [opt.strip() for opt in options_list]:
                raise forms.ValidationError("Ensure that the correct answer matches one of the options.")
        return cleaned_data