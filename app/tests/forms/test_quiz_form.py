from django.test import TestCase
from app.models import Quiz
from app.forms import QuizForm


class QuizFormTestCase(TestCase): #The last 3 of these fail, not sure what's up with the type field or why it won't save
    def setUp(self):
        self.form_input = {
            'name': 'Sample Quiz',
            'subject': 'Math',
            'difficulty': 'Medium'
        }

    def test_valid_quiz_form(self):
        form = QuizForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = QuizForm()
        self.assertIn('name', form.fields)
        self.assertIn('subject', form.fields)
        self.assertIn('difficulty', form.fields)
        self.assertIn('type', form.fields)

    def test_name_is_required(self):
        self.form_input['name'] = ''
        form = QuizForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_subject_is_required(self):
        self.form_input['subject'] = ''
        form = QuizForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('subject', form.errors)

    def test_difficulty_is_required(self):
        self.form_input['difficulty'] = ''
        form = QuizForm(data=self.form_input)
        self.assertTrue(form.is_valid())


    def test_form_save_creates_quiz(self):
        before_count = Quiz.objects.count()
        print(f'Before count: {before_count}')
        form = QuizForm(data=self.form_input)
        form.save()
        after_count = Quiz.objects.count()
        self.assertEqual(after_count, before_count + 1)
        quiz = Quiz.objects.get(name='Sample Quiz')
        self.assertEqual(quiz.name, 'Sample Quiz')
        self.assertEqual(quiz.subject, 'Math')
        self.assertEqual(quiz.difficulty, 'Medium')

    def test_type_field_is_optional(self):
        self.form_input['type'] = ''
        form = QuizForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        self.assertNotIn('type', form.errors)

    def test_type_field_is_optional_with_invalid_value(self):
        self.form_input['type'] = 'InvalidType'
        form = QuizForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        self.assertNotIn('type', form.errors)
