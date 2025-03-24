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
        self.assertFalse(form.is_valid())
        # The clean() method should add a non-field error.
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
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['options'], ['Python', 'JavaScript', 'C++'])

    def test_widget_rendering(self):
        # Test that the custom widget renders the expected HTML.
        widget = MultipleChoiceOptionsWidget()
        rendered_html = widget.render(name="options", value="Option1\nOption2")
        self.assertIn('name="options[]"', rendered_html)
        self.assertIn('Enter option', rendered_html)
