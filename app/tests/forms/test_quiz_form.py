from django.test import TestCase
from app.models import Quiz
from app.forms import QuizForm
from app.models.user import User

class QuizFormTestCase(TestCase): #The last 3 of these fail, not sure what's up with the type field or why it won't save
    def setUp(self):
        self.form_input = {
            'name': 'Sample Quiz',
            'subject': 'Math',
            'difficulty': 'M',
            'is_public': False
        }

    def test_valid_quiz_form(self):
        form = QuizForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = QuizForm()
        self.assertIn('name', form.fields)
        self.assertIn('subject', form.fields)
        self.assertIn('difficulty', form.fields)
        self.assertIn('is_public', form.fields)
        #test type once present in the form webpage

    def test_name_is_required(self):
        self.form_input['name'] = ''
        form = QuizForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertEqual(form.errors['name'][0], "Quiz name cannot be empty.")

    def test_subject_is_required(self):
        self.form_input['subject'] = ''
        form = QuizForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('subject', form.errors)
        self.assertEqual(form.errors['subject'][0], "Subject cannot be empty.")

    def test_difficulty_is_required(self):
        self.form_input['difficulty'] = ''
        form = QuizForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('difficulty', form.errors)
        self.assertEqual(form.errors['difficulty'][0], "Difficulty cannot be empty.")

    def test_form_save_creates_quiz(self):
        before_count = Quiz.objects.count()
        print(f'Before count: {before_count}')
        form = QuizForm(data=self.form_input)
        quiz = form.save(commit=False)
        tutor = User.objects.create_user(
        email_address='tutor@example.com',
        first_name='Test',
        last_name='Tutor',
        role=User.TUTOR
        )
        quiz.tutor = tutor
        quiz.save()
        after_count = Quiz.objects.count()
        self.assertEqual(after_count, before_count + 1)
        quiz = Quiz.objects.get(name='Sample Quiz')
        self.assertEqual(quiz.name, 'Sample Quiz')
        self.assertEqual(quiz.subject, 'Math')
        self.assertEqual(quiz.difficulty, 'M')
        self.assertEqual(quiz.is_public, False)
        self.assertEqual(quiz.type, '') #this should also be changed

#these are later tests when type field is insterted in the webpage

    #def test_type_field_is_optional(self):
        #self.form_input['type'] = ''
        #form = QuizForm(data=self.form_input)
        #self.assertTrue(form.is_valid())
        #self.assertNotIn('type', form.errors)

    #def test_type_field_is_optional_with_invalid_value(self):
        #self.form_input['type'] = 'InvalidType'
        #form = QuizForm(data=self.form_input)
        #self.assertTrue(form.is_valid())
        #self.assertNotIn('type', form.errors)
