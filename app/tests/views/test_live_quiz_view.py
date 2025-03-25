# import json, os
# from django import setup
# from django.test import TestCase
# from django.urls import reverse
# from django.contrib.auth import get_user_model
# from app.models import Room, Quiz, IntegerInputQuestion
# from channels.layers import get_channel_layer
# from channels.testing import ChannelsLiveServerTestCase, WebsocketCommunicator
# from asgiref.sync import async_to_sync, sync_to_async
# from app.consumers import LobbyConsumer, StudentQuizConsumer
#
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.quizsite.settings")
# setup()
# User = get_user_model()
#
# #Reminder to myself, fix issue where ChannelLiveServerTestCase can't be used in memory databases
#
# #Tests the student_live_quiz view and WebSocket communication.
# """
# class ViewTests(ChannelsLiveServerTestCase):
#
#
#     async def setUp(self):
#         # Create a student user
#         self.student_user = await sync_to_async(User.objects.create_user)(
#             first_name="Stu",
#             last_name="Dent",
#             email_address="student@example.com",
#             password="password123",
#             role=User.STUDENT,
#         )
#         # Create a tutor user
#         self.tutor_user = await sync_to_async(User.objects.create_user)(
#             first_name="Tu",
#             last_name = "Tor",
#             email_address="tutor@example.com",
#             password="password123",
#             role=User.TUTOR,
#         )
#         # Create a quiz
#         self.quiz = await sync_to_async(Quiz.objects.create)(
#             name="My Quiz",
#             type="Live",
#             tutor=self.tutor_user,
#         )
#         # Create a question
#         self.question = await sync_to_async(IntegerInputQuestion.objects.create)(
#             question_text="What is 2+2?",
#             correct_answer=4,
#             quiz=self.quiz,
#         )
#         #Create a room
#         self.test_room = await sync_to_async(Room.objects.create)(name = "Live Room for Testing",
#             quiz = self.quiz,
#             join_code = "TEST123"
#         )
#
#         self.channel_layer = get_channel_layer()
#
#     async def test_lobby_websocket_connection(self):
#         #Test if WebSocket connection works for LobbyConsumer.
#         communicator = WebsocketCommunicator(
#             LobbyConsumer.as_asgi(),
#             f"ws/lobby/{self.test_room.join_code}/"
#         )
#         connected, _ = await communicator.connect()
#         self.assertTrue(connected)
#
#         # Test sending an "update" action
#         await communicator.send_json_to({"action": "update"})
#         response = await communicator.receive_json_from()
#
#         # Validate response contains the expected participants list
#         self.assertIn("participants", response)
#         self.assertIsInstance(response["participants"], list)
#
#         await communicator.disconnect()
#
#     async def test_student_quiz_websocket_connection(self):
#         #Test if WebSocket connection works for StudentQuizConsumer.
#         communicator = WebsocketCommunicator(
#             StudentQuizConsumer.as_asgi(),
#             f"ws/live-quiz/{self.test_room.join_code}/"
#         )
#         connected, _ = await communicator.connect()
#         self.assertTrue(connected)  # Ensure connection is successful
#
#         # Simulate a tutor sending a quiz update message
#         message = {
#             "type": "quiz_update",
#             "message": {
#                 "question_text": "What is 2+2?",
#                 "correct_answer": "4"
#             }
#         }
#         await self.channel_layer.group_send(f"quiz_{self.test_room.join_code}", message)
#
#         # Check if the student received the question
#         response = await communicator.receive_json_from()
#         self.assertEqual(response, message["message"])
#         await communicator.disconnect()
#         """

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

    