from django.test import TestCase

from app.helpers.helper_functions import isCorrectAnswer,get_streak_bonus,get_speed_bonus,calculate_user_score, calculate_user_base_score
from app.models import User, TrueFalseQuestion, IntegerInputQuestion, NumericalRangeQuestion, TrueFalseResponse, Quiz, RoomParticipant, Response, Room, IntegerInputResponse, NumericalRangeResponse


class TestCalculateUserScore(TestCase):
    def setUp(self):
        # Creating a test user (a tutor)
        self.tutor = User.objects.create_user(
            email_address='tutor@example.com',
            first_name='Tutor',
            last_name='User',
            role=User.TUTOR
        )

        # Create a quiz linked to the tutor
        self.quiz = Quiz.objects.create(
            name="Sample Quiz",
            subject="General Knowledge",
            difficulty="E",  # Easy
            type="L",  # Live
            tutor=self.tutor
        )

        self.room = Room.objects.create(
            name="Test Room",
            quiz=self.quiz  # Associate the room with the quiz
        )

        self.player1 = User.objects.create_user(
            email_address='player1@email.com',
            first_name='Player1',
            last_name='User',
            role = User.STUDENT
        )

        self.player2 = User.objects.create_user(
            email_address='player2@email.com',
            first_name='Player2',
            last_name='User',
            role = User.STUDENT
        )
        self.room_participant1 = RoomParticipant.objects.create(user=self.player1, room=self.room)
        self.room_participant2 = RoomParticipant.objects.create(user=self.player2, room=self.room)

        # Create test questions
        self.tf_question = TrueFalseQuestion.objects.create(
            question_text="Is 2+2 equal to 4?",
            correct_answer=True,
            quiz=self.quiz,
            position=1,
            time=30,
            mark=5
        )

        self.int_question = IntegerInputQuestion.objects.create(
            question_text="What is 10 - 3?",
            correct_answer=7,
            quiz=self.quiz,
            position=2,
            time=30,
            mark=5
        )

        self.range_question = NumericalRangeQuestion.objects.create(
            question_text="Pick a number between 5 and 15.",
            min_value=5,
            max_value=15,
            quiz=self.quiz,
            position=3,
            time=30,
            mark=5
        )

    def test_correct_answer_updates_score(self):
        #player1 answers correctly
        response = TrueFalseResponse.objects.create(
            player=self.player1,
            room=self.room,
            question=self.tf_question,
            answer=True #correct answer
        )
        #ensure isCorrectAnswer() works
        self.assertTrue(isCorrectAnswer(response))
        #calculate the score
        score = calculate_user_base_score(self.player1, self.room)
        #check the players score update
        self.assertEqual(score,5) # speed bonus +3 is applied

    def test_correct_answer_updates_score_with_speed(self):
        #player1 answers correctly
        response = TrueFalseResponse.objects.create(
            player=self.player1,
            room=self.room,
            question=self.tf_question,
            answer=True #correct answer
        )
        #ensure isCorrectAnswer() works
        self.assertTrue(isCorrectAnswer(response))
        #calculate the score
        score = calculate_user_score(self.player1, self.room)
        #check the players score update
        self.assertEqual(score,8) # speed bonus +3 is applied

    def test_incorrect_answer_does_not_add_score(self):
        #player2 answers incorrectly
        response = TrueFalseResponse.objects.create(
            player=self.player2,
            room=self.room,
            question=self.tf_question,
            answer=False #wrong answer
        )
        #ensure isCorrectAnswer() works
        self.assertFalse(isCorrectAnswer(response))
        #calculate the score
        score = calculate_user_score(self.player1, self.room)
        #check the players score update
        self.assertEqual(score,0)

    def test_base_score(self):
        """Test that streak and speed bonuses are applied correctly together."""
        
        # Player1 answers three correct questions in a row (streak bonus applies)
        TrueFalseResponse.objects.create(player=self.player1, room=self.room, question=self.tf_question, answer=True)
        IntegerInputResponse.objects.create(player=self.player1, room=self.room, question=self.int_question, answer=7)  
        NumericalRangeResponse.objects.create(player=self.player1, room=self.room, question=self.range_question, answer=10)

        # Player2 answers later (speed bonus applies)
        TrueFalseResponse.objects.create(player=self.player2, room=self.room, question=self.tf_question, answer=True)

        # Calculate scores
        score1 = calculate_user_base_score(self.player1, self.room)
        score2 = calculate_user_base_score(self.player2, self.room)

        # Base Score: 5+5+5 = 15 
        expected_score1 = 15  # 15
        expected_score2 = 5   # 5

        self.assertEqual(score1, expected_score1)  # Player1 should have 15 points
        self.assertEqual(score2, expected_score2)  # Player2 should have 5 points

    
    def test_streak_and_speed_bonus(self):
        """Test that streak and speed bonuses are applied correctly together."""
        
        # Player1 answers three correct questions in a row (streak bonus applies)
        TrueFalseResponse.objects.create(player=self.player1, room=self.room, question=self.tf_question, answer=True)
        IntegerInputResponse.objects.create(player=self.player1, room=self.room, question=self.int_question, answer=7)  
        NumericalRangeResponse.objects.create(player=self.player1, room=self.room, question=self.range_question, answer=10)

        # Player2 answers later (speed bonus applies)
        TrueFalseResponse.objects.create(player=self.player2, room=self.room, question=self.tf_question, answer=True)

        # Calculate scores
        score1 = calculate_user_score(self.player1, self.room)
        score2 = calculate_user_score(self.player2, self.room)

        # Base Score: 5+5+5 = 15, Streak Bonus (3rd answer): 0.5 * 5 = 2, Speed Bonus (first answer): 3,Speed Bonus (second answer): 3,Speed Bonus (third answer): 3
        expected_score1 = 15 + 2 + 3 + 3 + 3 # 26
        expected_score2 = 5 + 2  # 7 (speed bonus for second responder)

        self.assertEqual(score1, expected_score1)  # Player1 should have 20 points
        self.assertEqual(score2, expected_score2)  # Player2 should have 7 points

    
