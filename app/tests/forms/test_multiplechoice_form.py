from django.http import QueryDict
from django.test import TestCase
from app.forms.multiple_choice_question_form import MultipleChoiceQuestionForm, MultipleChoiceOptionsWidget

class MultipleChoiceQuestionFormTest(TestCase):
    def test_valid_form_with_newline_options(self):
        qdict = QueryDict(mutable=True)
        # Simulate multiple POST values for options:
        qdict.setlist('options', ["Paris", "London", "Berlin"])
        qdict.update({
            'time': 30,
            'question_text': 'What is the capital of France?',
            'mark': 1,
            'correct_answer': "Paris",
        })
        form = MultipleChoiceQuestionForm(qdict)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['options'], ['Paris', 'London', 'Berlin'])

    def test_valid_form_with_list_options(self):
        qdict = QueryDict(mutable=True)
        qdict.setlist('options', ["Pink", "Blue", "Green"])
        qdict.update({
            'time': 45,
            'question_text': 'Which color is a mix of red and white?',
            'mark': 2,
            'correct_answer': "Pink",
        })
        form = MultipleChoiceQuestionForm(qdict)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['options'], ['Pink', 'Blue', 'Green'])

    def test_invalid_form_options_less_than_two(self):
        qdict = QueryDict(mutable=True)
        qdict.setlist('options', ["4"])  # Only one option provided.
        qdict.update({
            'time': 30,
            'question_text': 'What is 2+2?',
            'mark': 1,
            'correct_answer': "4",
        })
        form = MultipleChoiceQuestionForm(qdict)
    def test_invalid_time(self): #Fails
        form_data = {
            'time': 'abc',
            'question_text': 'What is 2 + 2?',
            'mark': 5,
            'options': '4\n3\n5\n2',
            'correct_answer': '4',
        }
        form = MultipleChoiceQuestionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('time', form.errors)
        self.assertEqual(form.errors['time'][0], "Time must be an integer.")

    def test_invalid_mark(self): #Fails
        form_data = {
            'time': 10,
            'question_text': 'What is 2 + 2?',
            'mark': 'abc',
            'options': '4\n3\n5\n2',
            'correct_answer': '4',
        }
        form = MultipleChoiceQuestionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('mark', form.errors)
        self.assertEqual(form.errors['mark'][0], "Mark must be an integer.")

    def test_options_with_less_than_two(self): #Fails
        form_data = {
            'time': 10,
            'question_text': 'What is 2 + 2?',
            'mark': 5,
            'options': '4',  # Only one option
            'correct_answer': '4',
        }
        form = MultipleChoiceQuestionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('options', form.errors)
        self.assertEqual(form.errors['options'], ["Please enter at least two options."])

    def test_invalid_form_incorrect_correct_answer(self):
        qdict = QueryDict(mutable=True)
        qdict.setlist('options', ["Jupiter", "Saturn", "Earth"])
        qdict.update({
            'time': 30,
            'question_text': 'What is the largest planet in our solar system?',
            'mark': 3,
            'correct_answer': "Mars",  # Incorrect answer; not in options.
        })
        form = MultipleChoiceQuestionForm(qdict)
    def test_correct_option_not_in_options(self): #Fails
        form_data = {
            'time': 10,
            'question_text': 'What is 2 + 2?',
            'mark': 5,
            'options': '4\n3\n5\n2',
            'correct_answer': '6',
        }
        form = MultipleChoiceQuestionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn(
            "Ensure that the correct answer matches one of the options.",
            form.errors['__all__']
        )

    def test_options_with_list_literal_string(self):
        qdict = QueryDict(mutable=True)
        # Simulate passing a list literal string.
        qdict.setlist('options', ["['Python', 'JavaScript', 'C++']"])
        qdict.update({
            'time': 30,
            'question_text': 'Which of the following are programming languages?',
            'mark': 2,
            'correct_answer': "Python",
        })
        form = MultipleChoiceQuestionForm(qdict)
    def test_correct_option_with_whitespace(self): #Fails
        form_data = {
            'time': 10,
            'question_text': 'What is 2 + 2?',
            'mark': 5,
            'options': '4\n3\n5\n2',
            'correct_answer': ' 4 ',  # Extra whitespace
        }
        form = MultipleChoiceQuestionForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['options'], ['Python', 'JavaScript', 'C++'])

    def test_widget_rendering(self):
        # Test that the custom widget renders the expected HTML.
        widget = MultipleChoiceOptionsWidget()
        rendered_html = widget.render(name="options", value="Option1\nOption2")
        self.assertIn('name="options[]"', rendered_html)
        self.assertIn('Enter option', rendered_html)

    def test_empty_options_field(self):
        form_data = {
            'time': 10,
            'question_text': 'Sample Question',
            'mark': 5,
            'options': '',
            'correct_answer': 'Option 1',
            'image': None
        }
        form = MultipleChoiceQuestionForm(data=form_data)

        self.assertFalse(form.is_valid())

        data = form_data
        widget = form.fields['options'].widget

        value = widget.value_from_datadict(data, {}, 'options')

        self.assertEqual(value, [''])

    def test_render_with_none_value(self):
        # Test when value is None
        widget = MultipleChoiceOptionsWidget()
        rendered_html = widget.render('options', None)

        # Check if the default value ["", ""] is used
        self.assertIn('<input type="text" name="options[]" value=""', rendered_html)
        self.assertIn('<input type="text" name="options[]" value=""', rendered_html)

    def test_render_with_string_value(self):
        # Test when value is a string
        widget = MultipleChoiceOptionsWidget()
        rendered_html = widget.render('options', "Option 1\nOption 2")

        # Check if the string is correctly split into two input fields
        self.assertIn('<input type="text" name="options[]" value="Option 1"', rendered_html)
        self.assertIn('<input type="text" name="options[]" value="Option 2"', rendered_html)

    def test_render_with_list_value(self):
        # Test when value is a list of options
        widget = MultipleChoiceOptionsWidget()
        rendered_html = widget.render('options', ["Option 1", "Option 2"])

    def test_clean_options_single_item_list(self):
        form_data = {
            'time': 10,
            'question_text': 'Sample Question',
            'mark': 5,
            'options': ['Option 1'],
            'correct_answer': 'Option 1',
            'image': None
        }
        form = MultipleChoiceQuestionForm(data=form_data)
        self.assertFalse(form.is_valid(), msg=f"Form errors: {form.errors}")

    def test_clean_options_single_item_list_with_nested_list(self):
        form_data = {
            'time': 10,
            'question_text': 'Sample Question',
            'mark': 5,
            'options': ['Option 1', '["Option 2a", "Option 2b"]'],
            'correct_answer': 'Option 1',
            'image': None
        }
        form = MultipleChoiceQuestionForm(data=form_data)

        self.assertTrue(form.is_valid(), msg=f"Form errors: {form.errors}")

    def test_clean_correct_answer_not_in_options(self):
        form_data = {
            'time': 10,
            'question_text': 'Sample Question',
            'mark': 5,
            'options': ['Option 1', 'Option 2'],
            'correct_answer': 'Option 3',
            'image': None
        }
        form = MultipleChoiceQuestionForm(data=form_data)

        self.assertFalse(form.is_valid(), msg=f"Form errors: {form.errors}")

        self.assertIn('Ensure that the correct answer matches one of the options.', form.non_field_errors())


