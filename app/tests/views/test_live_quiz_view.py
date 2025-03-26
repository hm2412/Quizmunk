import json
from unittest.mock import patch
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models import Room, Quiz, RoomParticipant, IntegerInputQuestion
from app.models import Question
from app.models.quiz_state import QuizState

User = get_user_model()

class LiveQuizViewTests(TestCase):
    def setUp(self):
        # Create a tutor user
        self.tutor_user = User.objects.create_user(
            first_name="Tu",
            last_name="Tor",
            email_address="tutor@example.com",
            password="password123",
            role=User.TUTOR,
        )
        
        # Create a student user
        self.student_user = User.objects.create_user(
            first_name="Stu",
            last_name="Dent",
            email_address="student@example.com",
            password="password123",
            role=User.STUDENT,
        )
        
        # Create a quiz
        self.quiz = Quiz.objects.create(
            name="Sample Quiz",
            tutor=self.tutor_user,  
        )

        self.question = IntegerInputQuestion.objects.create(
            question_text="What is 2+2?",
            mark=1,
            time=30,
            correct_answer=4,
            quiz=self.quiz,
        )
        
        # Create a room with a join code
        self.room = Room.objects.create(name="Sample Room", join_code="12345678", quiz=self.quiz)


    def test_tutor_can_access_live_quiz(self):
        """Tutor should be able to access live quiz page"""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("tutor_live_quiz", args=[self.quiz.id, self.room.join_code]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("tutor/live_quiz.html")

    def test_student_cannot_access_live_quiz(self):
        """Student should not be able to access live quiz page"""
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("tutor_live_quiz", args=[self.quiz.id, self.room.join_code]))
        self.assertEqual(response.status_code, 403)  


    def test_student_can_access_live_quiz(self):
        """Student should be able to access live quiz page"""
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("student_live_quiz", args=[self.room.join_code]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("student/student_live_quiz.html")

    def test_unauthenticated_student_can_access_live_quiz(self):
        """Unauthenticated student (guest) should be able to access live quiz page"""
        session = self.client.session
        session.create()  # Creating a session for the guest
        response = self.client.get(reverse("student_live_quiz", args=[self.room.join_code]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("student/student_live_quiz.html")

    def test_participant_count_in_live_quiz(self):
        """Ensure that the number of participants is displayed correctly"""
        self.client.login(email_address="student@example.com", password="password123")
        RoomParticipant.objects.create(room=self.room, user=self.student_user)  
        response = self.client.get(reverse("student_live_quiz", args=[self.room.join_code]))
        self.assertContains(response, str(self.room.participants.count()))

    def test_start_quiz_by_tutor(self):
        """Tutor should be able to start a quiz"""
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(reverse("start_quiz", args=[self.room.join_code]), data={})
        self.assertEqual(response.status_code, 302)  

    

    def test_next_question_for_tutor(self):
        """Test if the tutor can request the next question"""
        self.client.login(email_address="tutor@example.com", password="password123")

        QuizState.objects.create(room=self.room, quiz_started=True, current_question_index=0)

        response = self.client.post(reverse("next_question", args=[self.room.join_code]), data={})
        self.assertEqual(response.status_code, 200)  
        self.assertIn("question", response.json())   
        self.assertEqual(response.json()["question"], self.question.question_text)


    def test_next_question_for_student(self):
        """Test if the student can view the next question"""
        self.client.login(email_address="student@example.com", password="password123")

        QuizState.objects.create(room=self.room, quiz_started=True, current_question_index=0)

        response = self.client.post(reverse("next_question", args=[self.room.join_code]), data={})
        self.assertEqual(response.status_code, 200)  
        self.assertIn("question", response.json())   
        self.assertEqual(response.json()["question"], self.question.question_text)

    def test_end_quiz_by_tutor(self):
        """Test that the tutor can end the quiz"""
        self.client.login(email_address="tutor@example.com", password="password123")

        QuizState.objects.create(room=self.room, quiz_started=True, current_question_index=0)

        response = self.client.post(reverse("end_quiz", args=[self.room.join_code]), data={})
        self.assertEqual(response.status_code, 200)  

    def test_end_quiz_invalid_method(self):
        """Test that an invalid method (non-POST) returns an error"""
        # Send a GET request (which is not allowed)
        self.url = reverse('end_quiz', kwargs={'join_code': self.room.join_code})
        response = self.client.get(self.url)

        # Check that the response has the correct error message
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content.decode(), {"error": "Invalid request"})

    

    def test_unauthenticated_cannot_end_quiz(self):
        """Unauthenticated user cannot end the quiz"""
        response = self.client.post(reverse("end_quiz", args=[self.room.join_code]))
        self.assertEqual(response.status_code, 400) 

    def test_start_quiz_invalid_join_code(self):
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(reverse("start_quiz", args=["invalid_code"]))
        self.assertEqual(response.status_code, 404)

    def test_end_quiz_invalid_join_code(self):
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(reverse("end_quiz", args=["invalid_code"]))
        self.assertEqual(response.status_code, 404)

    def test_load_valid_partial(self):
        """Test loading a valid partial returns 200"""
        self.url = reverse('load_partial', kwargs={'partial_name': 'integer_input'})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/integer_input.html')

    def test_load_invalid_partial_raises_404(self):
        """Test loading an invalid partial raises 404"""
        self.url = reverse('load_partial', kwargs={'partial_name': 'integer_input'})
        invalid_url = reverse('load_partial', kwargs={'partial_name': 'invalid_partial'})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)



    def test_start_quiz_invalid_request(self):
        """Test that an invalid request (non-POST) returns an error response"""
        url = reverse('start_quiz', kwargs={'join_code': self.room.join_code})
        response = self.client.get(url)
        
        response_content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 400)

        self.assertJSONEqual(response_content, {"error": "Invalid request"})




    def test_next_question_no_quiz_started(self):
        """Test when the quiz has not started yet"""
        self.quiz_state = QuizState.objects.create(room=self.room, quiz_started=True, current_question_index=0)

        self.quiz_state.quiz_started = False
        self.quiz_state.save()

        self.client.login(email_address="student@example.com", password="password123")

        url = reverse('next_question', kwargs={'join_code': self.room.join_code})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 400)

        # Decode the response content before asserting equality
        response_content = response.content.decode('utf-8')
        self.assertJSONEqual(response_content, {"error": "Quiz has not started for this room."})

    def test_next_question_invalid_method(self):
        """Test that invalid methods (non-POST) return error"""
        url = reverse('next_question', kwargs={'join_code': self.room.join_code})

        response = self.client.get(url)  # GET request instead of POST

        self.assertEqual(response.status_code, 400)

        # Decode the response content before asserting equality
        # response_content = response.content.decode('utf-8')
        # self.assertJSONEqual(response_content, {"error": "Invalid request"})

    def test_no_more_questions(self):
        """Test that when all questions are answered, it returns no more questions message"""
        self.quiz_state = QuizState.objects.create(room=self.room, quiz_started=True, current_question_index=0)

        self.quiz_state.current_question_index = 1  # No more questions (only 1 available)
        self.quiz_state.save()

        self.client.login(email_address="student@example.com", password="password123")

        url = reverse('next_question', kwargs={'join_code': self.room.join_code})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)

        # Decode the response content before asserting equality
        response_content = response.content.decode('utf-8')
        self.assertJSONEqual(response_content, {"message": "No more questions!"})

    def test_guest_session_exists(self):
        """Test that a guest session is not created if it already exists"""
        # Set the session cookie manually
        #self.client.cookies[settings.SESSION_COOKIE_NAME] = 'existing_session_key'

        existing_session_key = self.client.session.session_key

        self.url = reverse('student_live_quiz', kwargs={'room_code': self.room.join_code})

        response = self.client.get(self.url)

        # Check that the session key is the same (no new session should be created)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.session_key, existing_session_key)

    def test_guest_session_created(self):
        """Test that a new guest session is created if it doesn't exist"""
        # Ensure the session does not exist yet
        self.client.session.clear()  # Clear the session

        self.url = reverse('student_live_quiz', kwargs={'room_code': self.room.join_code})

        # Make the request, which will create the session
        response = self.client.get(self.url)

        # Check that a new session key is created
        self.assertIsNotNone(self.client.session.session_key)
        self.assertNotEqual(self.client.session.session_key, '')

    