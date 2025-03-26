from django.test import TestCase
from app.forms.numerical_range_question_form import NumericalRangeQuestionForm


class NumericalRangeQuestionFormTest(TestCase):

    def test_clean_min_value_greater_than_max_value(self):
        form_data = {
            'time': 10,
            'question_text': 'Sample Question',
            'mark': 5,
            'min_value': 10,
            'max_value': 5,
            'image': None
        }
        form = NumericalRangeQuestionForm(data=form_data)

        self.assertFalse(form.is_valid(), msg=f"Form errors: {form.errors}")

        self.assertIn('Minimum value cannot be greater than maximum value.', form.errors.get('min_value', []))
        self.assertIn('Maximum value must be greater than or equal to the minimum value.',
                      form.errors.get('max_value', []))

    def test_clean_min_value_less_than_or_equal_to_max_value(self):
        form_data = {
            'time': 10,
            'question_text': 'Sample Question',
            'mark': 5,
            'min_value': 5,
            'max_value': 10,
            'image': None
        }
        form = NumericalRangeQuestionForm(data=form_data)

        self.assertTrue(form.is_valid(), msg=f"Form errors: {form.errors}")

    def test_clean_missing_min_value_or_max_value(self):
        form_data = {
            'time': 10,
            'question_text': 'Sample Question',
            'mark': 5,
            'min_value': None,  # No min_value
            'max_value': 10,  # Max value present
            'image': None
        }
        form = NumericalRangeQuestionForm(data=form_data)

        self.assertFalse(form.is_valid(), msg=f"Form errors: {form.errors}")

        form_data['min_value'] = 5  # Adding min_value now, test for no errors
        form = NumericalRangeQuestionForm(data=form_data)
        self.assertTrue(form.is_valid(), msg=f"Form errors: {form.errors}")

    def test_clean_both_values_missing(self):
        form_data = {
            'time': 10,
            'question_text': 'Sample Question',
            'mark': 5,
            'min_value': None,
            'max_value': None,
            'image': None
        }
        form = NumericalRangeQuestionForm(data=form_data)

        self.assertFalse(form.is_valid(), msg=f"Form errors: {form.errors}")
