from django.test import TestCase
from app.forms.decimal_input_question_form import DecimalInputQuestionForm
from decimal import Decimal

class DecimalInputQuestionFormTestCase(TestCase):

    def test_valid_decimal_input_form(self):
        data = {
            'time': 15,
            'question_text': 'What is 5/2?',
            'mark': 10,
            'correct_answer': Decimal('2.5'),
        }
        form = DecimalInputQuestionForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_time(self):
        data = {
            'time': 'abc',
            'question_text': 'What is 5/2?',
            'mark': 10,
            'correct_answer': Decimal('2.5'),
        }
        form = DecimalInputQuestionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('time', form.errors)
        self.assertEqual(form.errors['time'][0], "Time must be an integer.")

    def test_invalid_mark(self):
        data = {
            'time': 10,
            'question_text': 'What is 5/2?',
            'mark': 'xyz', 
            'correct_answer': Decimal('2.5'),
        }
        form = DecimalInputQuestionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('mark', form.errors)
        self.assertEqual(form.errors['mark'][0], "Mark must be an integer.")

    def test_invalid_correct_answer(self):
        data = {
            'time': 15,
            'question_text': 'What is 5/2?',
            'mark': 10,
            'correct_answer': 'two point five', 
        }
        form = DecimalInputQuestionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('correct_answer', form.errors)
        self.assertEqual(form.errors['correct_answer'][0], "Correct answer must be a decimal.")

    def test_blank_fields(self):
        data = {}
        form = DecimalInputQuestionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('time', form.errors)
        self.assertIn('question_text', form.errors)
        self.assertIn('mark', form.errors)
        self.assertIn('correct_answer', form.errors)

    def test_invalid_time_float(self):
        data = {
            'time': 10.5,
            'question_text': 'Test question?',
            'mark': 5,
            'correct_answer': Decimal('3.14'),
        }
        form = DecimalInputQuestionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('time', form.errors)
        self.assertEqual(form.errors['time'][0], "Time must be an integer.")
       