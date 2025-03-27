from itertools import count
from django.test import TestCase
from app.helpers.helper_functions import get_responses, get_responses_by_player_in_room, get_all_responses_question, \
    count_answers_for_question, get_streak_bonus, calculate_user_score, calculate_user_base_score, \
    get_leaderboard, create_quiz_stats, get_student_quiz_history, calculate_average_score, find_best_and_worst_scores, \
    getAllQuestions
from app.models import User, IntegerInputQuestion, Quiz, TrueFalseQuestion, TextInputQuestion, DecimalInputQuestion, \
    MultipleChoiceQuestion, NumericalRangeQuestion, Room, IntegerInputResponse, TrueFalseResponse, \
    RoomParticipant

class TestGetterHelpers(TestCase):
    def setUp(self):
        self.tutor = User.objects.create_user(
            email_address="tutor@example.com",
            first_name="John",
            last_name="Doe",
            password="password",
            role=User.TUTOR
        )
        self.student1 = User.objects.create_user(
            email_address="student1@example.com",
            first_name="Alice",
            last_name="Smith",
            password="password",
            role=User.STUDENT
        )
        self.student2 = User.objects.create_user(
            email_address="student2@example.com",
            first_name="Bob",
            last_name="Johnson",
            password="password",
            role=User.STUDENT
        )
        self.quiz = Quiz.objects.create(
            name="Sample Quiz",
            subject="Math",
            difficulty="M",  # Medium difficulty
            type="L",  # Live quiz
            is_public=True,
            tutor=self.tutor  # Associate quiz with the tutor
        )

        # Create one question of each type and link to the quiz

        # Integer Input Question
        self.integer_question = IntegerInputQuestion.objects.create(
            question_text="What is 2 + 2?",
            position=1,
            time=30,
            quiz=self.quiz,
            mark=1,
            correct_answer=4
        )

        # True/False Question
        self.true_false_question = TrueFalseQuestion.objects.create(
            question_text="Is the sky blue?",
            position=2,
            time=30,
            quiz=self.quiz,
            mark=1,
            correct_answer=True
        )

        # Text Input Question
        self.text_input_question = TextInputQuestion.objects.create(
            question_text="Fill in the blank: The capital of France is _____",
            position=3,
            time=30,
            quiz=self.quiz,
            mark=1,
            correct_answer="Paris"
        )

        # Decimal Input Question
        self.decimal_input_question = DecimalInputQuestion.objects.create(
            question_text="What is 10.5 + 2.3?",
            position=4,
            time=30,
            quiz=self.quiz,
            mark=1,
            correct_answer=12.8
        )

        # Multiple Choice Question
        self.mc_question = MultipleChoiceQuestion.objects.create(
            question_text="Which is the largest planet?",
            position=5,
            time=30,
            quiz=self.quiz,
            mark=1,
            options=["Earth", "Mars", "Jupiter", "Venus"],
            correct_answer="Jupiter"
        )

        # Numerical Range Question
        self.num_range_question = NumericalRangeQuestion.objects.create(
            question_text="Pick a number between 1 and 10",
            position=6,
            time=30,
            quiz=self.quiz,
            mark=1,
            min_value=1,
            max_value=10
        )

        self.room = Room.objects.create(
            name="Room",
            quiz=self.quiz,
        )

        RoomParticipant.objects.create(
            room=self.room,
            user=self.student1,
        )

        RoomParticipant.objects.create(
            room=self.room,
            user=self.student2,
        )

        self.int_response1 = IntegerInputResponse.objects.create(
            player=self.student1,
            room=self.room,
            question=self.integer_question,
            answer=4
        )

        self.int_response2 = IntegerInputResponse.objects.create(
            player=self.student2,
            room=self.room,
            question=self.integer_question,
            answer=3
        )

        self.tf_response1 = TrueFalseResponse.objects.create(
            player=self.student1,
            room=self.room,
            question=self.true_false_question,
            answer=False
        )

        self.tf_response2 = TrueFalseResponse.objects.create(
            player=self.student2,
            room=self.room,
            question=self.true_false_question,
            answer=True
        )

        create_quiz_stats(self.room)

    def test_count_responses(self):
        self.assertEqual(count_answers_for_question(self.room, self.integer_question), 2)
        self.assertEqual(count_answers_for_question(self.room, self.true_false_question), 2)
        self.assertEqual(count_answers_for_question(self.room, self.decimal_input_question), 0)
        self.assertEqual(count_answers_for_question(self.room, self.text_input_question), 0)
        self.assertEqual(count_answers_for_question(self.room, self.mc_question), 0)
        self.assertEqual(count_answers_for_question(self.room, self.num_range_question), 0)

    def test_count_responses_invalid_question(self):
        self.assertEqual(count_answers_for_question(self.room, self.quiz), 0)

    def test_get_streak_bonus(self):
        self.assertEqual(get_streak_bonus(5, 10), 10)
        self.assertEqual(get_streak_bonus(3, 20), 10)
        self.assertEqual(get_streak_bonus(4, 30), 0)

    def test_calculate_user_score(self):
        self.assertEqual(calculate_user_score(self.student1, self.room), 4)
        self.assertEqual(calculate_user_base_score(self.student1, self.room), 1)
        self.assertEqual(calculate_user_score(None, self.room), 0)

    def test_get_leaderboard(self):
        leaderboard=get_leaderboard(self.room)
        self.assertEqual(len(leaderboard), 2)
        self.assertEqual(get_leaderboard(None), [])

    def test_get_student_quiz_history(self):
        calculate_user_score(self.student1, self.room)
        quiz_history = get_student_quiz_history(self.student1)
        self.assertEqual(len(quiz_history), 1)
        self.assertEqual(quiz_history[0]['quiz_name'], self.quiz.name)
        self.assertEqual(quiz_history[0]['score'], 1)
        self.assertEqual(calculate_average_score(quiz_history), 1)
        best_score, worst_score = find_best_and_worst_scores(quiz_history)
        self.assertEqual(best_score['quiz_name'], self.quiz.name)
        self.assertEqual(worst_score['quiz_name'], self.quiz.name)

    def test_null_get_all_questions(self):
        self.assertIsNone(getAllQuestions(None))

    def test_invalid_calculate_average_score(self):
        self.assertEqual(calculate_average_score(None), 0)
