from django.test import TestCase
from django.core.exceptions import ValidationError
from app.models.quiz_state import QuizState
from app.models.room import Room
from app.models.quiz import Quiz
from app.models.user import User

class QuizStateTest(TestCase):
    def setUp(self):
        self.tutor = User.objects.create_user(
            email_address="tutor@email.com",
            password="password123",
            first_name="Test",
            last_name="Tutor",
            role=User.TUTOR
        )

        self.quiz = Quiz.objects.create(
            name="Test Quiz",
            subject="Math",
            difficulty="E",
            tutor=self.tutor
        )

        self.room = Room.objects.create(
            name="Test Room",
            quiz=self.quiz
        )

        self.quiz_state = QuizState.objects.create(
            room=self.room,
            current_question_index=0,
            quiz_started=False
        )

    def test_quiz_state_creation(self):
        self.assertEqual(self.quiz_state.current_question_index, 0)
        self.assertFalse(self.quiz_state.quiz_started)
        self.assertEqual(self.quiz_state.room, self.room)

    def test_next_question_increments_index(self):
        initial_index = self.quiz_state.current_question_index
        self.quiz_state.next_question()
        self.assertEqual(self.quiz_state.current_question_index, initial_index + 1)

    def test_quiz_state_unique_room(self):
        with self.assertRaises(Exception):
            QuizState.objects.create(
                room=self.room,
                current_question_index=0,
                quiz_started=False
            )

    def test_quiz_state_default_values(self):
        new_room = Room.objects.create(
            name="Another Test Room",
            quiz=self.quiz
        )
        quiz_state = QuizState.objects.create(room=new_room)
        self.assertEqual(quiz_state.current_question_index, 0)
        self.assertFalse(quiz_state.quiz_started)

    def test_quiz_state_updates(self):
        self.quiz_state.quiz_started = True
        self.quiz_state.current_question_index = 5
        self.quiz_state.save()
        
        updated_state = QuizState.objects.get(id=self.quiz_state.id)
        self.assertTrue(updated_state.quiz_started)
        self.assertEqual(updated_state.current_question_index, 5)

    def test_quiz_state_cascade_delete(self):
        room_id = self.room.id
        self.room.delete()
        self.assertFalse(QuizState.objects.filter(room_id=room_id).exists())
