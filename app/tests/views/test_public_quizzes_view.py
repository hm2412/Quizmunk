from django.test import TestCase, Client
from django.urls import reverse
from app.models import Quiz, User
from app.models.quiz import IntegerInputQuestion, MultipleChoiceQuestion

class PublicQuizzesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.tutor1 = User.objects.create_user(
            email_address="tutor1@example.com",
            first_name="Test",
            last_name="Tutor1",
            password="password1234",
            role=User.TUTOR
        )
        
        self.tutor2 = User.objects.create_user(
            email_address="tutor2@example.com",
            first_name="Test",
            last_name="Tutor2",
            password="password1234",
            role=User.TUTOR
        )

        self.student = User.objects.create_user(
            email_address="student@example.com",
            first_name="Test",
            last_name="Student",
            password="password1234",
            role=User.STUDENT
        )

        self.public_quiz = Quiz.objects.create(
            name="Public Quiz",
            subject="Math",
            difficulty="E",
            type="L",
            is_public=True,
            tutor=self.tutor1
        )

        self.private_quiz = Quiz.objects.create(
            name="Private Quiz",
            subject="Science",
            difficulty="M",
            type="L",
            is_public=False,
            tutor=self.tutor1
        )

    def test_public_quizzes_view_requires_login(self):
        response = self.client.get(reverse('public_quizzes'))
        self.assertRedirects(response, '/')

    def test_public_quizzes_view_requires_tutor(self):
        self.client.login(email_address="student@example.com", password="password1234")
        response = self.client.get(reverse('public_quizzes'))
        self.assertEqual(response.status_code, 403)

    def test_tutor_can_view_public_quizzes(self):
        self.client.login(email_address="tutor2@example.com", password="password1234")
        response = self.client.get(reverse('public_quizzes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/public_quizzes.html')
        self.assertIn(self.public_quiz, response.context['quizzes'])
        self.assertNotIn(self.private_quiz, response.context['quizzes'])

    def test_tutor_cannot_see_own_public_quizzes(self):
        self.client.login(email_address="tutor1@example.com", password="password1234")
        response = self.client.get(reverse('public_quizzes'))
        self.assertNotIn(self.public_quiz, response.context['quizzes'])

    def test_search_by_name(self):
        self.client.login(email_address="tutor2@example.com", password="password1234")
        response = self.client.get(f"{reverse('public_quizzes')}?name_search=Public")
        self.assertIn(self.public_quiz, response.context['quizzes'])
        
        response = self.client.get(f"{reverse('public_quizzes')}?name_search=Nonexistent")
        self.assertEqual(len(response.context['quizzes']), 0)

    def test_search_by_subject(self):
        self.client.login(email_address="tutor2@example.com", password="password1234")
        response = self.client.get(f"{reverse('public_quizzes')}?subject_search=Math")
        self.assertIn(self.public_quiz, response.context['quizzes'])
        
        response = self.client.get(f"{reverse('public_quizzes')}?subject_search=History")
        self.assertEqual(len(response.context['quizzes']), 0)

    def test_filter_by_difficulty(self):
        self.client.login(email_address="tutor2@example.com", password="password1234")
        response = self.client.get(f"{reverse('public_quizzes')}?difficulty=E")
        self.assertIn(self.public_quiz, response.context['quizzes'])
        
        response = self.client.get(f"{reverse('public_quizzes')}?difficulty=H")
        self.assertEqual(len(response.context['quizzes']), 0)

    def test_save_public_quiz(self):
        self.client.login(email_address="tutor2@example.com", password="password1234")
        response = self.client.get(reverse('save_public_quiz', args=[self.public_quiz.id]))
        
        new_quiz = Quiz.objects.get(name=f"Copy of {self.public_quiz.name}")
        self.assertEqual(new_quiz.subject, self.public_quiz.subject)
        self.assertEqual(new_quiz.difficulty, self.public_quiz.difficulty)
        self.assertEqual(new_quiz.tutor, self.tutor2)
        self.assertRedirects(response, reverse('edit_quiz', args=[new_quiz.id]))

    def test_quiz_preview_modal(self):
        self.client.login(email_address="tutor2@example.com", password="password1234")
        response = self.client.get(reverse('quiz_preview_modal', args=[self.public_quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/_quiz_preview_modal.html')
        self.assertEqual(response.context['quiz'], self.public_quiz)

    def test_cannot_preview_private_quiz(self):
        self.client.login(email_address="tutor2@example.com", password="password1234")
        response = self.client.get(reverse('quiz_preview_modal', args=[self.private_quiz.id]))
        self.assertEqual(response.status_code, 404)

    def test_cannot_save_private_quiz(self):
        self.client.login(email_address="tutor2@example.com", password="password1234")
        response = self.client.get(reverse('save_public_quiz', args=[self.private_quiz.id]))
        self.assertEqual(response.status_code, 404)

    def test_combined_filters(self):
        self.client.login(email_address="tutor2@example.com", password="password1234")
        url = f"{reverse('public_quizzes')}?name_search=Public&subject_search=Math&difficulty=E"
        response = self.client.get(url)
        self.assertIn(self.public_quiz, response.context['quizzes'])
        
        url = f"{reverse('public_quizzes')}?name_search=Public&subject_search=Math&difficulty=M"
        response = self.client.get(url)
        self.assertEqual(len(response.context['quizzes']), 0)
    
    def test_all_subjects_in_context(self):
        self.client.login(email_address="tutor2@example.com", password="password1234")
        response = self.client.get(reverse('public_quizzes'))
        self.assertIn('Math', response.context['all_subjects'])
        
    def test_empty_search_parameters(self):
        self.client.login(email_address="tutor2@example.com", password="password1234")
        response = self.client.get(reverse('public_quizzes'))
        self.assertIn(self.public_quiz, response.context['quizzes'])
        self.assertEqual(response.context['name_query'], '')
        self.assertEqual(response.context['subject_query'], '')
        self.assertEqual(response.context['difficulty'], '') 
        
    def test_quiz_with_questions(self):
        self.client.login(email_address="tutor2@example.com", password="password1234")
        

        
        
        IntegerInputQuestion.objects.create(
            quiz=self.public_quiz,
            question_text="Test question",
            correct_answer=42,
            mark=1,
            position=1
        )
        
        response = self.client.get(reverse('quiz_preview_modal', args=[self.public_quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['questions']) > 0)
        self.assertEqual(response.context['questions'][0].question_text, "Test question") 
        
    def test_student_cannot_save_public_quiz(self):
        self.client.login(email_address="student@example.com", password="password1234")
        response = self.client.get(reverse('save_public_quiz', args=[self.public_quiz.id]))
        self.assertEqual(response.status_code, 403) 
        
    def test_quiz_preview_with_multiple_choice_question(self):
        self.client.login(email_address="tutor2@example.com", password="password1234")
        
        
      
        MultipleChoiceQuestion.objects.create(
            quiz=self.public_quiz,
            question_text="Multiple choice test",
            options=["Option 1", "Option 2", "Option 3", "Option 4"],
            correct_answer="Option 2",
            mark=1,
            position=1
        )
        
        response = self.client.get(reverse('quiz_preview_modal', args=[self.public_quiz.id]))
        self.assertEqual(response.status_code, 200)
        
     
        questions = response.context['questions']
        self.assertTrue(len(questions) > 0)
        self.assertEqual(questions[0].question_text, "Multiple choice test")
        self.assertEqual(questions[0].options, ["Option 1", "Option 2", "Option 3", "Option 4"]) 
        
    def test_save_public_quiz_copies_questions(self):
        self.client.login(email_address="tutor2@example.com", password="password1234")
        
     
        
        original_question = IntegerInputQuestion.objects.create(
            quiz=self.public_quiz,
            question_text="Original question",
            correct_answer=42,
            mark=1,
            position=1
        )
        
      
        response = self.client.get(reverse('save_public_quiz', args=[self.public_quiz.id]))
        
      
        new_quiz = Quiz.objects.get(name=f"Copy of {self.public_quiz.name}")
        
        
        copied_questions = IntegerInputQuestion.objects.filter(quiz=new_quiz)
        self.assertEqual(copied_questions.count(), 1)
        self.assertEqual(copied_questions[0].question_text, "Original question")
        self.assertEqual(copied_questions[0].correct_answer, 42)
       
        self.assertNotEqual(copied_questions[0].id, original_question.id) 
        
