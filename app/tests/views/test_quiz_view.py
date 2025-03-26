import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.forms.quiz_form import QuizForm
from app.models.quiz import MultipleChoiceQuestion, Quiz, IntegerInputQuestion, TrueFalseQuestion
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class ViewTests(TestCase):
    def setUp(self):
        # Create a student user
        self.student_user = User.objects.create_user(
            first_name="Stu",
            last_name="Dent",
            email_address="student@example.com",
            password="password123",
            role=User.STUDENT,
        )
        # Create a tutor user
        self.tutor_user = User.objects.create_user(
            first_name="Tu",
            last_name = "Tor",
            email_address="tutor@example.com",
            password="password123",
            role=User.TUTOR,
        )
        # Create a quiz
        self.quiz = Quiz.objects.create(
            name="quiz1",
            subject="general",
            difficulty="E",
            type="L",
            is_public=False,
            tutor=self.tutor_user,
        )
        # Create a question
        self.integer_question = IntegerInputQuestion.objects.create(
            question_text="What is 2+2?",
            mark=1,
            time=30,
            correct_answer=4,
            quiz=self.quiz,
        )

        

    def test_tutor_can_access_create_quiz(self):
        """Tutors should be able to access the create quiz page"""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("create_quiz"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("tutor/create_quiz_form.html")

    def test_student_cannot_access_create_quiz(self):
        """Students should not be able to access the create quiz page"""
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("create_quiz"))
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cannot_access_create_quiz(self):
        """Unauthenticated users should not be able to access the create quiz page"""
        response = self.client.get(reverse("create_quiz"))
        self.assertEqual(response.status_code, 302)

    # def test_tutor_can_access_get_question(self):
    #     """Tutors should be able to access the create quiz page"""
    #     self.client.login(email_address="tutor@example.com", password="password123")
    #     response = self.client.get(reverse("get_question", args=[self.quiz.id]),  {'question_id': self.question.id})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed("tutor/create_quiz.html")

    

    def test_student_cannot_access_get_question(self):
        """Students should not be able to access the create quiz page"""
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("get_question", args=[self.quiz.id]),  {'question_id': self.integer_question.id})
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cannot_access_get_question(self):
        """Unauthenticated users should not be able to access the get question page"""
        response = self.client.get(reverse("get_question", args=[self.quiz.id]),  {'question_id': self.integer_question.id})
        self.assertEqual(response.status_code, 302)

    def test_tutor_can_access_edit_quiz_view(self):
        """Tutors should be able to access the edit quiz page"""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("edit_quiz", args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("tutor/edit_quiz.html")
        self.assertContains(response, self.quiz.name)
    
    def test_student_cannot_access_edit_quiz_view(self):
        """Student should not be able to access the edit quiz page"""
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("edit_quiz", args=[self.quiz.id]))
        self.assertEqual(response.status_code, 403)
    
    def test_unauthenticated_user_cannot_access_edit_quiz_view(self):
        """Unauthenticated users should not be able to access the edit quiz page"""
        response = self.client.get(reverse("edit_quiz", args=[self.quiz.id]))
        self.assertEqual(response.status_code, 302)

    def test_create_quiz_with_public_setting(self):
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(reverse("create_quiz"), {
            'name': 'New Quiz',
            'subject': 'Test Subject',
            'difficulty': 'E',
            'is_public': True
        })
        self.assertEqual(Quiz.objects.last().is_public, True)

    def test_create_quiz_with_private_setting(self):
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(reverse("create_quiz"), {
            'name': 'New Quiz',
            'subject': 'Test Subject',
            'difficulty': 'E',
            'is_public': False
        })
        self.assertEqual(Quiz.objects.last().is_public, False)

    def test_tutor_can_access_edit_quiz(self):
        """Tutor should access edit quiz page"""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("edit_quiz", args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tutor/edit_quiz.html")

    def test_tutor_can_delete_quiz(self):
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(reverse("delete_quiz", args=[self.quiz.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Quiz.objects.filter(id=self.quiz.id).exists())

    def test_tutor_can_delete_quiz_htmx(self):
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(
            reverse("delete_quiz", args=[self.quiz.id]),
            HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 204)

    def test_tutor_can_view_their_quizzes(self):
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("your_quizzes"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.quiz.name)

    

    def test_student_cannot_delete_question(self):
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.post(reverse("delete_question", args=["integer", self.integer_question.id]))
        self.assertEqual(response.status_code, 403)

    
    
    def test_student_cannot_delete_quiz(self):
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.post(reverse("delete_quiz", args=[self.quiz.id]))
        self.assertEqual(response.status_code, 403)

    def test_tutor_can_delete_question_image(self):
        self.integer_question.image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        self.integer_question.save()

        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(reverse("delete_question_image", args=["integer", self.integer_question.id]))
        self.assertEqual(response.status_code, 200)
        self.integer_question.refresh_from_db()
        self.assertFalse(self.integer_question.image)

    def test_student_cannot_access_get_question(self):
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("get_question", args=[self.quiz.id]), {
            'question_id': self.integer_question.id,
            'question_type': 'integer'
        })
        self.assertEqual(response.status_code, 403)

    def test_create_quiz_view_get(self):
        """Test GET request to create quiz view"""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse('create_quiz'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], QuizForm)

    

    def test_create_quiz_view_post_invalid(self):
        """Test creating a quiz with invalid data"""
        self.client.login(email_address="tutor@example.com", password="password123")
        
        # Intentionally provide invalid data
        quiz_data = {
            'name': '',  # Empty name should make form invalid
            'subject': '',
        }

        response = self.client.post(reverse('create_quiz'), quiz_data)
        self.assertEqual(response.status_code, 400)

    # def test_update_question_order(self):
    #     """Test updating question order"""
    #     self.client.login(email_address="tutor@example.com", password="password123")
        
    #     # Prepare order data
    #     order_data = {
    #         'quiz_id': self.quiz.id,
    #         'order': json.dumps([
    #             f'integer_input-{self.integer_question.id}',
    #             f'multiple_choice-{self.multiple_choice_question.id}'
    #         ])
    #     }

    #     response = self.client.post(reverse('update_question_order'), order_data)
    #     self.assertEqual(response.status_code, 200)
        
    #     # Refresh questions and check their new positions
    #     self.integer_question.refresh_from_db()
    #     self.multiple_choice_question.refresh_from_db()

    

    def test_get_question_view_invalid_params(self):
        """Test getting a question with invalid parameters"""
        self.client.login(email_address="tutor@example.com", password="password123")
        
        # Missing question_id
        response = self.client.get(reverse('get_question', args=[self.quiz.id]), {
            'question_type': 'integer'
        })
        self.assertEqual(response.status_code, 400)

        # Missing question_type
        response = self.client.get(reverse('get_question', args=[self.quiz.id]), {
            'question_id': self.integer_question.id
        })
        self.assertEqual(response.status_code, 400)

    def test_delete_quiz_unauthorized(self):
        """Test that another tutor or student cannot delete a quiz"""
        # Create another tutor
        another_tutor = User.objects.create_user(
            first_name="Another",
            last_name="Tutor",
            email_address="another_tutor@example.com",
            password="password123",
            role=User.TUTOR,
        )

        # Try to delete with a different tutor
        self.client.login(email_address="another_tutor@example.com", password="password123")
        response = self.client.post(reverse('delete_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 404)  # Should not find the quiz

        # Try to delete with a student
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.post(reverse('delete_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 403)

    

    def test_unauthenticated_get_question(self):
        """Test unauthenticated user cannot get question"""
        response = self.client.get(
            reverse('get_question', args=[self.quiz.id]), 
            {'question_id': self.integer_question.id, 'question_type': 'integer'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_student_cannot_get_question(self):
        """Test student cannot get question"""
        self.client.login(email_address="student@example.com", password="password123")
        
        response = self.client.get(
            reverse('get_question', args=[self.quiz.id]), 
            {'question_id': self.integer_question.id, 'question_type': 'integer'}
        )
        self.assertEqual(response.status_code, 403)

    def test_get_question_view_success(self):
        """Test retrieving a question successfully"""
        self.client.login(email_address="tutor@example.com", password="password123")
        
        response = self.client.get(
            reverse('get_question', args=[self.quiz.id]), 
            {'question_id': self.integer_question.id, 'question_type': 'integer'}
        )
        
        
        self.assertEqual(response.status_code, 200, 
            f"Expected 200, got {response.status_code}. Content: {response.content.decode('utf-8')}")
    
        
        data = json.loads(response.content)
        self.assertEqual(data['question_text'], "What is 2+2?")
        self.assertEqual(data['correct_answer'], 4)

    def test_delete_question(self):
        """Test deleting a question"""
        self.client.login(email_address="tutor@example.com", password="password123")
        
        response = self.client.post(
            reverse('delete_question', 
            args=['integer', self.integer_question.id])
        )

        
        
        self.assertEqual(response.status_code, 200, 
            f"Expected 200, got {response.status_code}. Content: {response.content.decode('utf-8')}")
        
        
        
        # Check question is deleted
        with self.assertRaises(IntegerInputQuestion.DoesNotExist):
            IntegerInputQuestion.objects.get(id=self.integer_question.id)

    # def test_create_quiz_view_post_valid(self):
    #     """Test creating a quiz with valid data"""
    #     self.client.force_login(self.tutor_user)  # Correct login method

    #     image_file = SimpleUploadedFile(
    #         name='test_image.jpg', 
    #         content=b'', 
    #         content_type='image/jpeg'
    #     )

    #     quiz_data = {
    #         'name': 'New Test Quiz',
    #         'subject': 'Science',
    #         'difficulty': 'E',
    #         'type': 'L',
    #         'is_public': False,
    #         'quiz_img': image_file
    #     }

    #     response = self.client.post(
    #         reverse('create_quiz'),
    #         data=quiz_data,
    #         content_type='multipart/form-data'
    #     )

    #     print("Create Quiz Response:", response.status_code, response.content.decode())

    #     self.assertIn(response.status_code, [400, 302, 200])
        
    #     new_quiz = Quiz.objects.filter(name='New Test Quiz').first()
    #     self.assertIsNotNone(new_quiz)
    #     self.assertEqual(new_quiz.tutor, self.tutor_user)


    def test_edit_quiz_view_get(self):
        """Test GET request to edit quiz page"""
        url = reverse('edit_quiz', kwargs={'quiz_id': self.quiz.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/edit_quiz.html')
        self.assertContains(response, "Sample Quiz")

    def test_edit_quiz_post_valid_multiple_choice_question(self):
        """Test POST with valid multiple choice question form"""
        url = reverse('edit_quiz', kwargs={'quiz_id': self.quiz.id})
        question_data = {
            'multiple_choice': 'true',  # Simulates the form type detection
            'quizID': self.quiz.id,
            'question_text': 'What is 2 + 2?',
            'option_a': '3',
            'option_b': '4',
            'option_c': '5',
            'option_d': '6',
            'correct_option': 'B'
        }
        response = self.client.post(url, data=question_data)

        # Should redirect back to edit_quiz
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url)

        # Ensure the question was created and linked to the quiz
        question = MultipleChoiceQuestion.objects.filter(quiz=self.quiz, question_text='What is 2 + 2?').first()
        self.assertIsNotNone(question)
        self.assertEqual(question.correct_option, 'B')

    def test_edit_quiz_post_invalid_data(self):
        """Test POST with invalid data - missing required field"""
        url = reverse('edit_quiz', kwargs={'quiz_id': self.quiz.id})
        question_data = {
            'multiple_choice': 'true',
            'quizID': self.quiz.id,
            # 'question_text' is missing - should trigger form invalid
            'option_a': '3',
            'option_b': '4',
            'option_c': '5',
            'option_d': '6',
            'correct_option': 'B'
        }
        response = self.client.post(url, data=question_data)

        # Should re-render with form errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/edit_quiz.html')
        self.assertContains(response, 'This field is required.')

    def test_edit_quiz_htmx_redirect(self):
        """Test HTMX POST request returns HX-Redirect header"""
        url = reverse('edit_quiz', kwargs={'quiz_id': self.quiz.id})
        question_data = {
            'multiple_choice': 'true',
            'quizID': self.quiz.id,
            'question_text': 'HTMX Question?',
            'option_a': 'Yes',
            'option_b': 'No',
            'option_c': 'Maybe',
            'option_d': 'IDK',
            'correct_option': 'A'
        }
        response = self.client.post(url, data=question_data, HTTP_HX_REQUEST='true')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('HX-Redirect', response.headers)

    def test_edit_quiz_view_unauthorized_user(self):
        """Test that a non-owner cannot edit another tutor's quiz"""
        other_tutor = User.objects.create_user(email_address="other_tutor@example.com", password="password123", role='Tutor')
        self.client.logout()
        self.client.login(email_address="other_tutor@example.com", password="password123")

        url = reverse('edit_quiz', kwargs={'quiz_id': self.quiz.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)  # Should raise 404 because they don't own the quiz



    
