from django.test import TestCase
from app.forms.true_false_question_form import TrueFalseQuestionForm

class TrueFalseQuestionFormTestCase(TestCase):
    def test_valid_true_false_form(self):
        """Test that valid data makes the true/false form valid."""
        data = {
            'time': 10,
            'question_text': 'Is the sky blue?',
            'correct_answer': True,
            'mark': 5,
        }
        form = TrueFalseQuestionForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['time'], 10)
        self.assertEqual(form.cleaned_data['mark'], 5)
        self.assertTrue(form.cleaned_data['correct_answer'])
    
    def test_invalid_time_in_true_false(self):
        """Test that non-integer time triggers an error in the true/false form."""
        data = {
            'time': 'not an integer',
            'question_text': 'Is the sky blue?',
            'correct_answer': True,
            'mark': 5,
        }
        form = TrueFalseQuestionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('time', form.errors)
        self.assertEqual(form.errors['time'][0], "Time must be an integer.")
    
    def test_invalid_mark_in_true_false(self):
        """Test that non-integer mark triggers an error in the true/false form."""
        data = {
            'time': 10,
            'question_text': 'Is the sky blue?',
            'correct_answer': True,
            'mark': 'not an integer',
        }
        form = TrueFalseQuestionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('mark', form.errors)
        self.assertEqual(form.errors['mark'][0], "Mark must be an integer.")
