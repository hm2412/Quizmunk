from django.test import TestCase
from app.forms.text_input_question_form import TextInputQuestionForm

class TextInputQuestionFormTestCase(TestCase):
    def test_valid_text_input_form(self):
        data = {
            'time': 15,
            'question_text': 'What the colour of the sky?',
            'mark': 10,
            'correct_answer': 'Blue',
        }
        form = TextInputQuestionForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['time'], 15)
        self.assertEqual(form.cleaned_data['mark'], 10)
        self.assertEqual(form.cleaned_data['correct_answer'], 'Blue')
    
    def test_invalid_time(self):
        data = {
            'time': 'abc',
            'question_text': 'What the colour of the sky?',
            'mark': 10,
            'correct_answer': 'Blue',
        }
        form = TextInputQuestionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('time', form.errors)
        self.assertEqual(form.errors['time'][0], "Time must be an integer.")
    
    def test_invalid_mark(self):
        data = {
            'time': 15,
            'question_text': 'What the colour of the sky?',
            'mark': 'xyz',
            'correct_answer': 'Blue',
        }
        form = TextInputQuestionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('mark', form.errors)
        self.assertEqual(form.errors['mark'][0], "Mark must be an integer.")