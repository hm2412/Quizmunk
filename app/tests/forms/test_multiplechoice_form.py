from django.test import TestCase
from app.forms.multiple_choice_question_form import MultipleChoiceQuestionForm

class MultipleChoiceQuestionFormTest(TestCase):

    def test_valid_multiple_choiceform(self):
        form_data = {
            'time': 10,
            'question_text': 'What is 2 + 2?',
            'mark': 5,
            'options': '4\n3\n5\n2',
            'correct_answer': '4',
        }
        form = MultipleChoiceQuestionForm(data=form_data)
        self.assertTrue(form.is_valid())

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
        self.assertIn('correct_answer', form.errors)

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
