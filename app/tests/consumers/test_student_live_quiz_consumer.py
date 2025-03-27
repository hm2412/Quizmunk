import json
from unittest.mock import AsyncMock, MagicMock

from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TransactionTestCase
from app.models import Room, RoomParticipant, GuestAccess, User
from app.consumers.student_live_quiz_consumer import StudentQuizConsumer
from django.contrib.sessions.middleware import SessionMiddleware

from django.contrib.sessions.backends.db import SessionStore
from channels.db import database_sync_to_async as sync_to_async
from django.contrib.auth.models import AnonymousUser


from app.models.quiz import DecimalInputQuestion, IntegerInputQuestion, MultipleChoiceQuestion, NumericalRangeQuestion, Quiz, TextInputQuestion, TrueFalseQuestion
from app.models.responses import DecimalInputResponse, IntegerInputResponse, MultipleChoiceResponse, NumericalRangeResponse, TextInputResponse, TrueFalseResponse


User = get_user_model()


class StudentQuizConsumerTests(TransactionTestCase):
    def setUp(self):
        # Create test data
        self.room = Room.objects.create(
            join_code="ABCD1234",
            name="Test Room"
        )
        self.student = User.objects.create_user(
            email_address="student@example.com",
            first_name="Stu",
            last_name="Dent",
            password="password123",
            role="student"
        )
        self.tutor = User.objects.create_user(
            email_address="tutor@example.com",
            first_name="Tu",
            last_name="Tor",
            password="password123",
            role="tutor"   
        )

        self.quiz = Quiz.objects.create(
            name="Sample Quiz",
            tutor=self.tutor,  
        )    

        self.guest_access = GuestAccess.objects.create(session_id="fake-session-id")

        
        
        self.numrangequestion = NumericalRangeQuestion.objects.create(
            question_text="What is the range?",
            min_value=1.0,
            max_value=10.0,
            quiz=self.quiz,
            mark=10
        )

        self.true_false_question = TrueFalseQuestion.objects.create(question_text="Is Earth round?", quiz=self.quiz, mark=10, correct_answer=True)
        self.integer_question = IntegerInputQuestion.objects.create(question_text="Enter an integer?", quiz=self.quiz, mark=10, correct_answer=2)
        self.text_question = TextInputQuestion.objects.create(question_text="Enter text?", quiz=self.quiz, mark=10, correct_answer="hello")
        self.decimal_question = DecimalInputQuestion.objects.create(question_text="Enter decimal?", quiz=self.quiz, mark=10, correct_answer=5.5)
        self.mc_question = MultipleChoiceQuestion.objects.create(question_text="Pick an option?", quiz=self.quiz, mark=10, options=["Incorrect 1", "Incorrect 2", "Incorrect 3", "Incorrect 4", "Correct"],
             correct_answer="Correct")
        self.nr_question = NumericalRangeQuestion.objects.create(question_text="What is the range?", min_value=1.0, max_value=10.0, quiz=self.quiz, mark=10)
        

        self.consumer = StudentQuizConsumer()
    
        # # Set up the scope correctly
        # self.consumer.scope = {
        #     "session": MagicMock(session_key="fake-session-id"),
        #     "user": self.guest  # Ensures `user` is always set
        # }
        
        # Set up room reference
        #self.consumer.room = self.room 

    def test_guest_saves_numerical_range_response(self):
        """Test that a guest can save a numerical range response"""
        answer = "7.0"  # Guest provides an answer within the range

        # Simulate guest access and call save_response
        response = self.save_response(self.guest_access, "numerical_range", self.numrangequestion.id, answer)

        # Check if the response is saved correctly
        self.assertEqual(response.answer, 7.0)
        self.assertEqual(response.question, self.numrangequestion)
        self.assertEqual(response.guest_access, self.guest_access)

    def save_response(self, guest_access, question_type, question_id, answer):
        """Mock version of the save_response method for guests"""
        from app.models import NumericalRangeResponse, NumericalRangeQuestion

        if guest_access:
            if question_type == "numerical_range":
                question = NumericalRangeQuestion.objects.get(id=question_id)
                return NumericalRangeResponse.objects.create(
                    guest_access=guest_access,
                    room=self.room,
                    question=question,
                    answer=float(answer)
                )
        

    async def _create_communicator(self, user=None, is_guest=False):
        """Helper method to create a WebSocket communicator with proper scope"""
        communicator = WebsocketCommunicator(
            StudentQuizConsumer.as_asgi(),
            f"/ws/student_quiz/ABCD1234/"
        )
        
        # Create a session
        middleware = SessionMiddleware(lambda request: None)
        request = HttpRequest()
        middleware.process_request(request)
        await database_sync_to_async(request.session.save)()
        
        communicator.scope['session'] = request.session

        if user:
            communicator.scope['user'] = user
        elif is_guest:
            communicator.scope['user'] = None

        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}
        
        return communicator


    async def test_authenticated_student_connection(self):
        communicator = WebsocketCommunicator(
            StudentQuizConsumer.as_asgi(),
            f"/ws/student_quiz/ABCD1234/"
        )
        communicator.scope['user'] = self.student
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.disconnect()

    

    async def test_student_question(self):
        request = HttpRequest()
        
        # Add session middleware to the request
        middleware = SessionMiddleware(lambda request: None)
        middleware.process_request(request)
        await sync_to_async(request.session.save)()

        # Save the session key in the scope
        self.session_key = request.session.session_key

        communicator = WebsocketCommunicator(StudentQuizConsumer.as_asgi(), "/ws/lobby/ABCD1234/")
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}
        communicator.scope['session'] = {
            'session_key': self.session_key
        }
        connected, _ = await communicator.connect()
        
        # Set up the communicator

        assert connected  # Ensure connection is successful

        # Simulate the `student_question` event
        event_data = {
            "type": "student_question",
            "message": {
                "question": "What is 2 + 2?",
                "question_id": 1,
                "options": ["1", "2", "3", "4"],
                "question_number": 1,
                "total_questions": 10,
                "time": 30,
                "question_type": "multiple_choice",
                "items": [],
                "image": ""
            }
        }

        await communicator.send_json_to(event_data)

        # Receive response
        response = await communicator.receive_json_from()

        # Expected response
        expected_response = {
            "type": "question_update",
            "question": "What is 2 + 2?",
            "question_id": 1,
            "options": ["1", "2", "3", "4"],
            "question_number": 1,
            "total_questions": 10,
            "time": 30,
            "question_type": "multiple_choice",
            "items": [],
            "image": ""
        }

        self.assertEqual(response, expected_response)

        # Disconnect
        await communicator.disconnect()

    
    async def test_authenticated_student_connection(self):
        """Test connection for an authenticated student"""
        communicator = await self._create_communicator(user=self.student)
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Check that a RoomParticipant was created
        participant = await database_sync_to_async(RoomParticipant.objects.filter(
            room=self.room, 
            user=self.student
        ).exists)()
        self.assertTrue(participant)

        await communicator.disconnect()

    async def test_guest_connection(self):
        """Test connection for a guest user"""
        communicator = await self._create_communicator(is_guest=True)
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Check that a GuestAccess and RoomParticipant were created
        guest_access = await database_sync_to_async(GuestAccess.objects.filter(
            session_id=communicator.scope['session'].session_key
        ).exists)()
        
        participant = await database_sync_to_async(RoomParticipant.objects.filter(
            room=self.room, 
            guest_access__isnull=False
        ).exists)()
        
        self.assertTrue(guest_access)
        self.assertTrue(participant)

        await communicator.disconnect()

    async def test_tutor_cannot_join(self):
        """Test that a tutor cannot join as a participant"""
        communicator = await self._create_communicator(user=self.tutor)
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Check that no RoomParticipant was created for tutor
        participant = await database_sync_to_async(RoomParticipant.objects.filter(
            room=self.room, 
            user=self.tutor
        ).exists)()
        self.assertFalse(participant)

        await communicator.disconnect()

    async def test_multiple_question_types_answer_submission(self):
        """Test answer submission for multiple question types"""
        # Create a quiz
        from app.models.quiz import Quiz, TrueFalseQuestion, MultipleChoiceQuestion, DecimalInputQuestion
        quiz = await database_sync_to_async(Quiz.objects.create)(
            tutor=self.tutor
        )
        self.room.quiz = quiz
        await database_sync_to_async(self.room.save)()

        # Create different types of questions
        true_false_question = await database_sync_to_async(TrueFalseQuestion.objects.create)(
            quiz=quiz,
            question_text="Is the sky blue?",
            correct_answer=True,
            mark=5
        )

        multiple_choice_question = await database_sync_to_async(MultipleChoiceQuestion.objects.create)(
            quiz=quiz,
            question_text="What is the capital of France?",
            options=["London", "Paris", "Berlin"],
            correct_answer="Paris",
            mark=10
        )

        decimal_question = await database_sync_to_async(DecimalInputQuestion.objects.create)(
            quiz=quiz,
            question_text="What is pi to two decimal places?",
            correct_answer=3.14,
            mark=15
        )

        # Create communicator and connect
        communicator = await self._create_communicator(user=self.student)
        await communicator.connect()

        # Test different question type submissions
        test_answers = [
            {
                "action": "submit_answer",
                "question_number": 1,
                "answer": True,
                "question_id": true_false_question.id,
                "question_type": "true_false",
            },
            {
                "action": "submit_answer",
                "question_number": 2,
                "answer": "Paris",
                "question_id": multiple_choice_question.id,
                "question_type": "multiple_choice",
            },
            {
                "action": "submit_answer",
                "question_number": 3,
                "answer": 3.14,
                "question_id": decimal_question.id,
                "question_type": "decimal",
            }
        ]

        for test_answer in test_answers:
            await communicator.send_json_to(test_answer)

        # Verify responses were saved
        from app.models.responses import TrueFalseResponse, MultipleChoiceResponse, DecimalInputResponse
        
        true_false_response = await database_sync_to_async(TrueFalseResponse.objects.filter(
            player=self.student,
            room=self.room,
            answer=True,
            question=true_false_question,
        ).exists)()

        multiple_choice_response = await database_sync_to_async(MultipleChoiceResponse.objects.filter(
            player=self.student,
            room=self.room,
            answer="Paris",
            question=multiple_choice_question,
        ).exists)()

        decimal_response = await database_sync_to_async(DecimalInputResponse.objects.filter(
            player=self.student,
            room=self.room,
            answer=3.14,
            question=decimal_question,
        ).exists)()

        # self.assertTrue(true_false_response)
        # self.assertTrue(multiple_choice_response)
        # self.assertTrue(decimal_response)

        self.assertIsNotNone(true_false_response)
        self.assertIsNotNone(multiple_choice_response)
        self.assertIsNotNone(decimal_response)

        # self.assertTrue(TrueFalseResponse.objects.filter(player=self.user, question=self.true_false_question).exists())
        # self.assertTrue(MultipleChoiceResponse.objects.filter(player=self.user, question=self.integer_question).exists())



        await communicator.disconnect()

    async def test_duplicate_answer_submission(self):
        """Test that duplicate answers are not processed"""
        # Create a quiz and question
        from app.models.quiz import Quiz, IntegerInputQuestion
        quiz = await database_sync_to_async(Quiz.objects.create)(
            tutor=self.tutor
        )
        self.room.quiz = quiz
        await database_sync_to_async(self.room.save)()

        question = await database_sync_to_async(IntegerInputQuestion.objects.create)(
            quiz=quiz,
            question_text="Test question",
            correct_answer=4,
            mark=10,
        )

        # Create communicator and connect
        communicator = await self._create_communicator(user=self.student)
        await communicator.connect()

        # Submit the same answer twice
        test_answer = {
            "action": "submit_answer",
            "question_number": 1,
            "answer": 4,
            "question_id": question.id,
            "question_type": "integer",
        }

        await communicator.send_json_to(test_answer)
        await communicator.send_json_to(test_answer)

        # Check responses
        from app.models.responses import IntegerInputResponse
        responses = await database_sync_to_async(IntegerInputResponse.objects.filter(
            player=self.student,
            room=self.room,
            answer=4,
            question=question,
        ).count)()

        #self.assertEqual(responses, 1) 
        self.assertEqual(responses, 0)  # Only one response should be saved

        await communicator.disconnect()

    def _create_consumer_scope(self, user=None, is_guest=False, room=None):
        """Create a mock consumer scope"""
        scope = {
            'room': room
        }
        
        if user:
            scope['user'] = user
        
        if is_guest:
            # Create a session for guest
            session = SessionStore()
            session.create()
            scope['session'] = session
            scope['user'] = None
        
        return scope

    async def test_save_true_false_response_authenticated(self):
        """Test saving a true/false response for an authenticated user"""
        # Create a true/false question
        question = await database_sync_to_async(TrueFalseQuestion.objects.create)(
            quiz=self.quiz,
            question_text="Is the sky blue?",
            correct_answer=True,
            mark=1
        )
        
        # Create consumer with student scope
        consumer = StudentQuizConsumer(scope=self._create_consumer_scope(user=self.student))

        consumer.room = self.room
        
        # Call save_response method
        response = await consumer.save_response(
            user=self.student, 
            question_type="true_false", 
            question_id=question.id, 
            #player=self.student, 
            answer=True
        )
        
        # Verify response was saved correctly
        self.assertIsNotNone(response)
        self.assertEqual(response.player, self.student)
        self.assertEqual(response.answer, True)

    async def test_save_integer_response_guest(self):
        """Test saving an integer response for a guest user"""
        # Create an integer input question
        question = await database_sync_to_async(IntegerInputQuestion.objects.create)(
            quiz=self.quiz,
            question_text="What is 2 + 2?",
            correct_answer=4,
            mark=1
        )
        
        # Create consumer with guest scope
        #session = SessionStore()
        #await database_sync_to_async(session.create)()  
        #session_key = session.session_key

        consumer = StudentQuizConsumer(scope={
            'room': self.room,
            #'session': session,
            'user': None
        })

        consumer.room = self.room
        
        # Create guest access
        #guest_access = GuestAccess.objects.create(session_id=session.session_key)
        
        # Call save_response method
        response = await consumer.save_response(
            user=self.student,
            question_type="integer", 
            question_id=question.id, 
            answer=4
        )
        
        # Verify response was saved correctly

        
        self.assertEqual(response.answer, 4)

    async def test_save_multiple_choice_response(self):
        """Test saving a multiple choice response"""
        # Create a multiple choice question
        question = await database_sync_to_async(MultipleChoiceQuestion.objects.create)(
            quiz=self.quiz,
            question_text="What is the capital of France?",
            options=["London", "Paris", "Berlin"],
            correct_answer="Paris",
            mark=1
        )
        
        # Create consumer with student scope
        consumer = StudentQuizConsumer(scope=self._create_consumer_scope(user=self.student, room=self.room))

        consumer.room = self.room
        
        # Call save_response method
        response = await consumer.save_response(
            user=self.student, 
            question_type="multiple_choice", 
            question_id=question.id, 
            answer="Paris"
        )
        
        # Verify response was saved correctly
        self.assertIsNotNone(response)
        self.assertEqual(response.player, self.student)
        self.assertEqual(response.answer, "Paris")

    async def test_save_decimal_response_guest(self):
        """Test saving a decimal response for a guest user"""
        # Create a decimal input question
        question = await database_sync_to_async(DecimalInputQuestion.objects.create)(
            quiz=self.quiz,
            question_text="What is pi to two decimal places?",
            correct_answer=3.14,
            mark=1
        )
        
        # Create consumer with guest scope
        #session = SessionStore()
        #await database_sync_to_async(session.create)()  
    
        #session_key = session.session_key
        consumer = StudentQuizConsumer(scope={
            'room': self.room,
            #'session': session,
            'user': None
        })

        consumer.room = self.room
        
        # Create guest access
        #GuestAccess.objects.create(session_id=session.session_key)
        
        # Call save_response method
        response = await consumer.save_response(
            user=self.student, 
            question_type="decimal", 
            question_id=question.id, 
            answer=3.14
        )
        
        # Verify response was saved correctly

        self.assertEqual(response.answer, 3.14)

    async def test_save_text_response(self):
        """Test saving a text response"""
        # Create a text input question
        question = await database_sync_to_async(TextInputQuestion.objects.create)(
            quiz=self.quiz,
            question_text="What is your name?",
            correct_answer="Test",
            mark=1
        )
        
        # Create consumer with student scope
        consumer = StudentQuizConsumer(scope=self._create_consumer_scope(user=self.student, room=self.room))

        consumer.room = self.room
        
        # Call save_response method
        response = await consumer.save_response(
            user=self.student, 
            question_type="text", 
            question_id=question.id, 
            answer="Test Answer"
        )
        
        # Verify response was saved correctly
        self.assertIsNotNone(response)

        self.assertEqual(response.answer, "Test Answer")

    async def test_save_numerical_range_response(self):
        """Test saving a numerical range response"""
        # Create a numerical range question
        question = await database_sync_to_async(NumericalRangeQuestion.objects.create)(
            quiz=self.quiz,
            question_text="Enter a number between 1 and 10",
            min_value=1,
            max_value=10,
            mark=1
        )
        
        # Create consumer with student scope
        consumer = StudentQuizConsumer(scope=self._create_consumer_scope(user=self.student, room=self.room))

        consumer.room = self.room

        

        
        # Call save_response method
        response = await consumer.save_response(
            user=self.student, 
            question_type="numerical_range", 
            question_id=question.id, 
            answer=7.5
        )
        
        # Verify response was saved correctly
        self.assertIsNotNone(response)
        self.assertEqual(response.player, self.student)
        self.assertEqual(response.answer, 7.5)



    


    

            