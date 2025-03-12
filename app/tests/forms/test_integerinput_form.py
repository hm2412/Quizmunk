from django.test import TestCase
from app.forms.integer_input_question_form import IntegerInputQuestionForm

class IntegerInputQuestionFormTestCase(TestCase):
    def test_valid_integer_input_form(self):
        data = {
            'time': 15,
            'question_text': 'What is 7+8?',
            'mark': 10,
            'correct_answer': 15,
        }
        form = IntegerInputQuestionForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['time'], 15)
        self.assertEqual(form.cleaned_data['mark'], 10)
        self.assertEqual(form.cleaned_data['correct_answer'], 15)
    
    def test_invalid_time(self):
        data = {
            'time': 'abc',
            'question_text': 'What is 7+8?',
            'mark': 10,
            'correct_answer': 15,
        }
        form = IntegerInputQuestionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('time', form.errors)
        self.assertEqual(form.errors['time'][0], "Time must be an integer.")
    
    def test_invalid_mark(self):
        data = {
            'time': 15,
            'question_text': 'What is 7+8?',
            'mark': 'xyz',
            'correct_answer': 15,
        }
        form = IntegerInputQuestionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('mark', form.errors)
        self.assertEqual(form.errors['mark'][0], "Mark must be an integer.")
    
    def test_invalid_correct_answer(self):
        data = {
            'time': 15,
            'question_text': 'What is 7+8?',
            'mark': 10,
            'correct_answer': 'nope',
        }
        form = IntegerInputQuestionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('correct_answer', form.errors)
        self.assertEqual(form.errors['correct_answer'][0], "Correct answer must be an integer.")