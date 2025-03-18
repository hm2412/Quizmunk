import json, os
from django import setup
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models import Room, Quiz, IntegerInputQuestion
from channels.layers import get_channel_layer
from channels.testing import ChannelsLiveServerTestCase, WebsocketCommunicator
from asgiref.sync import async_to_sync, sync_to_async
from app.consumers import LobbyConsumer, StudentQuizConsumer


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.quizsite.settings")
setup()
User = get_user_model()

#Reminder to myself, fix issue where ChannelLiveServerTestCase can't be used in memory databases

#Tests the student_live_quiz view and WebSocket communication.
"""
class ViewTests(ChannelsLiveServerTestCase):
    

    async def setUp(self):
        # Create a student user
        self.student_user = await sync_to_async(User.objects.create_user)(
            first_name="Stu",
            last_name="Dent",
            email_address="student@example.com",
            password="password123",
            role=User.STUDENT,
        )
        # Create a tutor user
        self.tutor_user = await sync_to_async(User.objects.create_user)(
            first_name="Tu",
            last_name = "Tor",
            email_address="tutor@example.com",
            password="password123",
            role=User.TUTOR,
        )
        # Create a quiz
        self.quiz = await sync_to_async(Quiz.objects.create)(
            name="My Quiz",
            type="Live",
            tutor=self.tutor_user,
        )
        # Create a question
        self.question = await sync_to_async(IntegerInputQuestion.objects.create)(
            question_text="What is 2+2?",
            correct_answer=4,
            quiz=self.quiz,
        )
        #Create a room
        self.test_room = await sync_to_async(Room.objects.create)(name = "Live Room for Testing", 
            quiz = self.quiz, 
            join_code = "TEST123"
        )

        self.channel_layer = get_channel_layer()

    async def test_lobby_websocket_connection(self):
        #Test if WebSocket connection works for LobbyConsumer.
        communicator = WebsocketCommunicator(
            LobbyConsumer.as_asgi(),
            f"ws/lobby/{self.test_room.join_code}/"
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Test sending an "update" action
        await communicator.send_json_to({"action": "update"})
        response = await communicator.receive_json_from()
        
        # Validate response contains the expected participants list
        self.assertIn("participants", response)
        self.assertIsInstance(response["participants"], list)

        await communicator.disconnect()

    async def test_student_quiz_websocket_connection(self):
        #Test if WebSocket connection works for StudentQuizConsumer.
        communicator = WebsocketCommunicator(
            StudentQuizConsumer.as_asgi(),
            f"ws/live-quiz/{self.test_room.join_code}/"
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)  # Ensure connection is successful
        
        # Simulate a tutor sending a quiz update message
        message = {
            "type": "quiz_update",
            "message": {
                "question_text": "What is 2+2?",
                "correct_answer": "4"
            }
        }
        await self.channel_layer.group_send(f"quiz_{self.test_room.join_code}", message)

        # Check if the student received the question
        response = await communicator.receive_json_from()
        self.assertEqual(response, message["message"])
        await communicator.disconnect()
        """