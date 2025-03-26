from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from app.helpers.helper_functions import isCorrectAnswer, create_quiz_stats, get_response_model_class, \
    get_all_responses_question, get_responses_by_player_in_room
from app.models import User, TrueFalseQuestion, IntegerInputQuestion, NumericalRangeQuestion, TrueFalseResponse, Quiz, \
    Room, NumericalRangeResponse, Stats, IntegerInputResponse
from app.models.stats import QuestionStats

class TestStatsHelpers(TestCase):
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
            name="Sample Room",
            quiz=self.quiz
        )

        # Create questions for the quiz
        self.tf_question = TrueFalseQuestion.objects.create(
            question_text='Is this a true/false question?',
            correct_answer=True,
            quiz=self.quiz,
            position=1,
            time=30,
            mark=1
        )

        self.int_question = IntegerInputQuestion.objects.create(
            question_text='What is 2+2?',
            correct_answer=4,
            quiz=self.quiz,
            position=2,
            time=30,
            mark=1
        )

        self.num_range_question = NumericalRangeQuestion.objects.create(
            question_text='Pick a number between 10 and 20.',
            min_value=10.0,
            max_value=20.0,
            quiz=self.quiz,
            position=3,
            time=30,
            mark=1
        )

        self.player = User.objects.create_user(
            email_address='fake@email.com',
            first_name='Fake',
            last_name='User',
            role = User.STUDENT
        )
        self.tf_response = TrueFalseResponse.objects.create(question=self.tf_question, answer=True, player=self.player, room=self.room)
        self.num_range_response = NumericalRangeResponse.objects.create(question=self.num_range_question, answer=13, player=self.player, room=self.room)

    def test_create_quiz_stats(self):
        create_quiz_stats(self.room)

        stats = Stats.objects.get(room=self.room)
        self.assertEqual(stats.quiz, self.quiz)

        question_stats = QuestionStats.objects.filter(room=self.room)
        print(question_stats)

    def test_get_response_model_class(self):
        tf_content_type = ContentType.objects.get_for_model(self.tf_question)
        int_content_type = ContentType.objects.get_for_model(self.int_question)
        num_range_content_type = ContentType.objects.get_for_model(self.num_range_question)

        self.assertEqual(get_response_model_class(tf_content_type), TrueFalseResponse)
        self.assertEqual(get_response_model_class(int_content_type), IntegerInputResponse)
        self.assertEqual(get_response_model_class(num_range_content_type), NumericalRangeResponse)

        with self.assertRaises(ValueError):
            get_response_model_class(ContentType.objects.get_for_model(Quiz))

    def test_get_all_responses_question(self):
        responses = get_all_responses_question(self.room, self.tf_question)
        self.assertIn(self.tf_response, responses)
        self.assertEqual(responses.count(), 1)

        responses = get_all_responses_question(self.room, self.num_range_question)
        self.assertIn(self.num_range_response, responses)
        self.assertEqual(responses.count(), 1)

    def test_get_responses_by_player_in_room(self):
        responses = get_responses_by_player_in_room(self.player, self.room)

        self.assertIn(self.tf_response, responses)
        self.assertIn(self.num_range_response, responses)

        self.assertEqual(len(responses), 2)
        self.assertEqual(len(get_responses_by_player_in_room(self.quiz, self.room)), 0)
