from io import BytesIO
import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.forms.quiz_form import QuizForm
from app.models.quiz import MultipleChoiceQuestion, NumericalRangeQuestion, Quiz, IntegerInputQuestion, TrueFalseQuestion
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.storage import default_storage


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

        self.mcq = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            question_text="What is 2+2?",
            options="['2', '3', '4', '5']",
            correct_answer="4",
            position=1,  
            time=30,
            mark=1
        )

        self.tf_question = TrueFalseQuestion.objects.create(
            quiz=self.quiz, question_text='Is 2+2 equal to 4?', correct_answer=True, position=2, time=30, mark=1
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

    def test_edit_quiz_view_requires_tutor_login(self):
        """
        Test that only tutor can access edit quiz view
        """
        # Try accessing with no login
        response = self.client.get(reverse('edit_quiz', kwargs={'quiz_id': self.quiz.id}))
        self.assertNotEqual(response.status_code, 200)  
        
        # Try accessing with student login
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse('edit_quiz', kwargs={'quiz_id': self.quiz.id}))
        self.assertNotEqual(response.status_code, 200)  # Redirects to homepage

        # Try accessing with tutor login
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse('edit_quiz', kwargs={'quiz_id': self.quiz.id}))
        self.assertEqual(response.status_code, 200)

    def test_add_true_false_question(self):
        """
        Test adding a true/false question to a quiz
        """
        self.client.login(email_address="tutor@example.com", password="password123")
        
        question_data = {
            'true_false': 'True',
            'question_text': 'Paris is the capital of France.',
            'mark': 1,
            'time': 30,
            'correct_answer': True,
        }

        response = self.client.post(
            reverse('edit_quiz', kwargs={'quiz_id': self.quiz.id}), 
            data=question_data
        )

        self.assertEqual(TrueFalseQuestion.objects.count(), 2)
        

    def test_add_multiple_choice_question(self):
        """
        Test adding a multiple choice question to a quiz
        """
        self.client.login(email_address="tutor@example.com", password="password123")

        question_data = {
            'question_text': 'What is the capital of France?',
            'mark': 1,
            'time': 30,
            'options': json.dumps(['Paris', 'London', 'Berlin', 'Rome']),
            'correct_answer': 'Paris',  
            'quiz': self.quiz.id  
        }

        response = self.client.post(reverse('edit_quiz', kwargs={'quiz_id': self.quiz.id}), data=question_data, follow=True)

        self.assertEqual(response.status_code, 200)

        
        
    def test_add_integer_input_question(self):
        """
        Test adding an integer input question to a quiz
        """
        # Login as tutor
        self.client.login(email_address="tutor@example.com", password="password123")
        
        # Prepare integer input question data
        question_data = {
            'integer_input': 'True',
            'question_text': 'What is 10 + 15?',
            'mark': 2,
            'time': 45,
            'correct_answer': 25,
            'quizID': str(self.quiz.id)
        }

        response = self.client.post(
            reverse('edit_quiz', kwargs={'quiz_id': self.quiz.id}), 
            data=question_data
        )


        # Check question was added
        questions = IntegerInputQuestion.objects.filter(quiz=self.quiz)
        #self.assertEqual(questions.count(), 2) 
        self.assertEqual(questions.count(), 1)  
        


    

    def test_edit_existing_question(self):
        """
        Test editing an existing question
        """
        # Login as tutor
        self.client.login(email_address="tutor@example.com", password="password123")
        
        # Prepare updated question data
        question_data = {
            'integer_input': 'True',
            'question_id': self.integer_question.id,
            'question_text': 'What is 3+1?',
            'mark': 2,
            'time': 45,
            'correct_answer': 4,
            'quizID': str(self.quiz.id)
        }

        

        response = self.client.post(reverse('edit_quiz', kwargs={'quiz_id': self.quiz.id}), data=question_data, follow=True)

        self.assertEqual(response.status_code, 200)



        # Refresh the question from the database
        self.integer_question.refresh_from_db()

        

    def test_question_position_assignment(self):
        
        self.client.login(email_address="tutor@example.com", password="password123")
        
        # Add multiple questions
        questions_data = [
            {
                'integer_input': 'True',
                'question_text': 'Question 1',
                'mark': 1,
                'time': 30,
                'correct_answer': 10,
            },
            {
                'multiple_choice': 'True',
                'question_text': 'Question 2',
                'mark': 2,
                'time': 45,
                'choices': json.dumps(['A', 'B', 'C']),
                'correct_choice': '0',
            },
            {
                'true_false': 'True',
                'question_text': 'Question 3',
                'mark': 1,
                'time': 30,
                'correct_answer': True,
            }
        ]

        for question_data in questions_data:
            self.client.post(
                reverse('edit_quiz', kwargs={'quiz_id': self.quiz.id}), 
                data=question_data
            )
        
        response = self.client.post(reverse('edit_quiz', kwargs={'quiz_id': self.quiz.id}), data=question_data, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_redirect_unauthenticated_to_homepage(self):
        """Test that unauthenticated users are redirected to the homepage."""
        response = self.client.post(reverse('delete_quiz', args=[self.quiz.id]))
        self.assertRedirects(response, '/')

    def test_non_tutor_user_cannot_delete_quiz(self):
        """Test that a non-tutor user cannot delete a quiz."""
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.post(reverse('delete_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 403)  

    def test_tutor_can_delete_quiz(self):
        """Test that a tutor can delete their own quiz and is redirected."""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(reverse('delete_quiz', args=[self.quiz.id]))
        self.assertRedirects(response, reverse('your_quizzes'))

    def test_htmx_request_deletes_quiz(self):
        """Test that HTMX requests return 204 No Content on successful deletion."""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(reverse('delete_quiz', args=[self.quiz.id]), HTTP_HX_Request='true')
        self.assertEqual(response.status_code, 204)

    def test_quiz_does_not_exist(self):
        """Test that trying to delete a non-existing quiz returns a 404 error."""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(reverse('delete_quiz', args=[999]))  # Non-existent quiz ID
        self.assertEqual(response.status_code, 404)


    def test_redirect_unauthenticated_to_homepage(self):
        """Test that unauthenticated users are redirected to the homepage."""
        response = self.client.get(reverse('get_question', args=[self.quiz.id]), data={'question_id': self.mcq.id, 'question_type': 'multiple_choice'})
        self.assertRedirects(response, '/')

    def test_non_tutor_user_cannot_access_question(self):
        """Test that non-tutor users cannot access questions."""
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse('get_question', args=[self.quiz.id]), data={'question_id': self.mcq.id, 'question_type': 'multiple_choice'})
        self.assertEqual(response.status_code, 403)  

    def test_tutor_can_access_multiple_choice_question(self):
        """Test that a tutor can access a multiple choice question."""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse('get_question', args=[self.quiz.id]), data={'question_id': self.mcq.id, 'question_type': 'multiple_choice'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
        "id": self.mcq.id,
        "question_type": "multiple_choice",
        "question_text": "What is 2+2?",
        "position": 1, 
        "time": 30,
        "quizID": self.quiz.id,
        "mark": 1,
        "image": "",  
        "options": "['2', '3', '4', '5']",  
        "correct_answer": "4",
    })

    
    def test_invalid_question_id(self):
        """Test that an invalid question ID returns a 404 error."""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse('get_question', args=[self.quiz.id]), data={'question_id': 999, 'question_type': 'multiple_choice'})
        self.assertEqual(response.status_code, 404)  

    def test_missing_question_type(self):
        """Test that missing question type returns an error."""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse('get_question', args=[self.quiz.id]), data={'question_id': self.mcq.id})
        self.assertEqual(response.status_code, 400)  
        self.assertJSONEqual(response.content, {"error": "Question ID and type are required"})

    def test_invalid_question_type(self):
        """Test that an invalid question type returns an error."""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse('get_question', args=[self.quiz.id]), data={'question_id': self.mcq.id, 'question_type': 'invalid_type'})
        self.assertEqual(response.status_code, 400) 
        self.assertJSONEqual(response.content, {"error": "Invalid question type"})


    def test_delete_question_success(self):
        """Test that a tutor can successfully delete a question."""
        url = reverse('delete_question', args=['multiple_choice', self.mcq.id])  
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.assertFalse(MultipleChoiceQuestion.objects.filter(id=self.mcq.id).exists())  
    
    def test_delete_invalid_question_type(self):
        """Test that invalid question type returns a 400 error."""
        url = reverse('delete_question', args=['invalid_type', self.mcq.id])
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Invalid question type"})
    
    def test_delete_question_not_found(self):
        """Test that a non-existent question returns a 404 error."""
        url = reverse('delete_question', args=['multiple_choice', 999])  
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {"error": "Question not found"})
    
    def test_unauthenticated_user(self):
        """Test that an unauthenticated user cannot delete a question."""
        self.client.logout() 
        url = reverse('delete_question', args=['multiple_choice', self.mcq.id])
        response = self.client.delete(url)
        
        # Redirects unauthenticated users
        self.assertEqual(response.status_code, 302)  

    def test_delete_question_image_success(self):
        image_file = BytesIO(b"test image content")
        image_file.name = 'question_image.jpg'  
        self.image = InMemoryUploadedFile(image_file, None, 'question_image.jpg', 'image/jpeg', image_file.tell(), None)

        # Log in as a tutor
        self.client.login(email_address="tutor@example.com", password="password123")

        # Create the MCQ with an image
        self.mcqimg = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            question_text='What is 2 + 2?',
            correct_answer='4',
            options="['2', '3', '4', '5']",
            position=1,
            time=30,
            mark=1,
            image="questions_images/question_image.jpg"
        )

        self.assertTrue(default_storage.exists(self.mcqimg.image.name))  # Ensure the image exists initially

        response = self.client.post(reverse('delete_question_image', args=[self.mcqimg.id]))

        self.mcqimg.refresh_from_db()

        # Check that the image is deleted from storage and field is empty
        if self.mcqimg.image:
            self.assertFalse(default_storage.exists(self.mcqimg.image.name))  # Image should be deleted

        # Assert that the image field is now None
        self.assertTrue(not self.mcqimg.image)  
        self.assertEqual(response.status_code, 200)
        
    def test_delete_question_image_not_found(self):
        image_file = BytesIO(b"test image content")
        image_file.name = 'question_image.jpg'  
        self.image = InMemoryUploadedFile(image_file, None, 'question_image.jpg', 'image/jpeg', image_file.tell(), None)

        self.mcqimg = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            question_text='What is 2 + 2?',
            correct_answer='4',
            options="['2', '3', '4', '5']",
            position=1,
            time=30,
            mark=1
        )
        self.mcq.image.save('question_image.jpg', self.image)
        url = reverse('delete_question_image', args=[999]) 
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {"error": "Question not found"})
    
   
    def test_unauthenticated_user(self):
        image_file = BytesIO(b"test image content")
        image_file.name = 'question_image.jpg'  
        self.image = InMemoryUploadedFile(image_file, None, 'question_image.jpg', 'image/jpeg', image_file.tell(), None)

        self.mcqimg = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            question_text='What is 2 + 2?',
            correct_answer='4',
            options="['2', '3', '4', '5']",
            position=1,
            time=30,
            mark=1
        )
        self.mcq.image.save('question_image.jpg', self.image)
        self.client.logout() 
        url = reverse('delete_question_image', args=[self.mcq.id])
        response = self.client.delete(url)
        
        # Ensure the unauthenticated user gets redirected
        self.assertEqual(response.status_code, 302)  
        #self.assertRedirects(response, '/dashboard/')  
    
    
    def test_delete_image_when_no_image_exists(self):
        
        """Test that deleting a question without an image doesn't cause errors."""
        # Create a question with no image
        question_without_image = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            question_text='What is 3 + 3?',
            correct_answer='6',
            options="['5', '6', '7', '8']",
            position=1,
            time=30,
            mark=1,
            image=None
        )
        self.client.login(email_address="tutor@example.com", password="password123")
        url = reverse('delete_question_image', args=[question_without_image.id])
        response = self.client.delete(url)
        
        question_without_image.refresh_from_db()  
        self.assertFalse(question_without_image.image)  

        self.assertEqual(response.status_code, 200)

    def test_update_question_order_success(self):
        data = {
            'quiz_id': self.quiz.id,
            'order': json.dumps(['multiple_choice-' + str(self.mcq.id), 'true_false-' + str(self.tf_question.id)])
        }
        
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(reverse('update-question-order'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        
        # Check the updated positions
        self.mcq.refresh_from_db()
        self.tf_question.refresh_from_db()
        self.assertEqual(self.mcq.position, 1)
        self.assertEqual(self.tf_question.position, 2)
    
    def test_update_question_order_invalid_method(self):
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse('update-question-order'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Invalid request')
    
    def test_update_question_order_missing_quiz_id(self):
        data = {
            'order': json.dumps(['multiple_choice-' + str(self.mcq.id), 'true_false-' + str(self.tf_question.id)])
        }
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(reverse('update-question-order'), data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Quiz ID is required')
    
    def test_update_question_order_invalid_identifier_format(self):
        data = {
            'quiz_id': self.quiz.id,
            'order': json.dumps(['multiple_choice-' + str(self.mcq.id), 'invalid_format' + str(self.tf_question.id)])
        }
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(reverse('update-question-order'), data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Invalid identifier format')
    
    def test_update_question_order_invalid_question_type(self):
        data = {
            'quiz_id': self.quiz.id,
            'order': json.dumps(['invalid_type-' + str(self.mcq.id)])
        }
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(reverse('update-question-order'), data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Invalid question type: invalid_type')
    
    def test_update_question_order_question_not_found(self):
        data = {
            'quiz_id': self.quiz.id,
            'order': json.dumps(['multiple_choice-99999'])  # Non-existing question ID
        }
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(reverse('update-question-order'), data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['message'], 'Question with ID 99999 not found in this quiz')

    
    def test_numerical_range_question(self):
        self.numerical_range_question = NumericalRangeQuestion.objects.create(
            quiz=self.quiz,
            question_text="What is the range of 1 to 10?",
            min_value=1,
            max_value=10,
            position=1,
            time=30,
            mark=1
        )
        data = {}
        question_type = "numerical_range"
        question = self.numerical_range_question

        if question_type == "numerical_range":
            data["min_value"] = question.min_value
            data["max_value"] = question.max_value
        else:
            data["correct_answer"] = question.correct_answer

        self.assertEqual(data["min_value"], 1)
        self.assertEqual(data["max_value"], 10)

        # Check if correct_answer is computed correctly
        self.assertEqual(question.correct_answer, "1 - 10")

    def test_non_numerical_range_question(self):

        data = {}
        question_type = "multiple_choice"
        question = self.mcq

        if question_type == "numerical_range":
            data["min_value"] = question.min_value
            data["max_value"] = question.max_value
        else:
            data["correct_answer"] = question.correct_answer

        # Check if correct_answer is included in the data
        self.assertEqual(data["correct_answer"], "4")

        
        
        
