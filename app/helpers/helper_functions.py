
from django.contrib.contenttypes.models import ContentType

from app.models import Quiz, IntegerInputQuestion, Response, TrueFalseQuestion, NumericalRangeResponse, RoomParticipant, \
    TextInputQuestion, DecimalInputQuestion, MultipleChoiceQuestion, NumericalRangeQuestion, SortingQuestion, quiz, \
    Stats, IntegerInputResponse, TrueFalseResponse, TextInputResponse, DecimalInputResponse, MultipleChoiceResponse, \
    SortingResponse
from app.models.stats import QuestionStats


def getAllQuestions(quiz):
    if isinstance(quiz, Quiz):
        questions_int = list(IntegerInputQuestion.objects.filter(quiz=quiz))
        questions_tf = list(TrueFalseQuestion.objects.filter(quiz=quiz))
        questions_text = list(TextInputQuestion.objects.filter(quiz=quiz))
        questions_decimal = list(DecimalInputQuestion.objects.filter(quiz=quiz))
        questions_mcq = list(MultipleChoiceQuestion.objects.filter(quiz=quiz))
        questions_num_range = list(NumericalRangeQuestion.objects.filter(quiz=quiz))
        questions_sorting = list(SortingQuestion.objects.filter(quiz=quiz))

        all_questions = (
            questions_int + questions_tf + questions_text +
            questions_decimal + questions_mcq + questions_num_range + questions_sorting
        )

        return all_questions
    return None


def isCorrectAnswer(response):
    if isinstance(response, NumericalRangeResponse):

        if response.question.min_value <= response.answer <= response.question.max_value:
            response.correct = True
            return True
        else:
            response.correct = False
            return False
    else:
        if response.answer == response.question.correct_answer:
            response.correct = True
            return True
        else:
            response.correct = False
            return False

def get_speed_bonus(position):
    """Calculate the bonus based on the response position."""
    if position==1:
        return 3
    elif 2<=position<=5:
        return 2
    elif 6<=position<=10:
        return 1
    return 0

def get_responses(user, room):
    #get all the responses for the specific user for a particular room ordered by time
    tf_responses = TrueFalseResponse.objects.filter(player=user, room=room)
    int_responses = IntegerInputResponse.objects.filter(player=user, room=room)
    text_responses = TextInputResponse.objects.filter(player=user, room=room)
    decimal_responses = DecimalInputResponse.objects.filter(player=user, room=room)
    mc_responses = MultipleChoiceResponse.objects.filter(player=user, room=room)
    range_responses = NumericalRangeResponse.objects.filter(player=user, room=room)
    sorting_responses = SortingResponse.objects.filter(player=user, room=room)
    responses = sorted(
        chain(tf_responses, int_responses, text_responses, decimal_responses, mc_responses, range_responses, sorting_responses),
        key=lambda r: r.timestamp  # Order by timestamp
    )
    return responses


def calculate_user_base_score(user,room):
    if not user or not room:
        return 0
    responses= get_responses(user,room)
    base_score=0 # base score ie without bonuses
    for response in responses:
        if isCorrectAnswer(response):
            base_score += response.question.mark  # add base points to base score
    return base_score

def calculate_user_score(user,room):
    if not user or not room:
        return 0
    responses= get_responses(user,room)
    base_score=0 # base score ie without bonuses
    total_score=0 #score including bonuses 
    streak_count=0 # streak tracker
    question_position={} # stores counters for each question
    print(f"\n--- Debugging Score Calculation for {user.email_address} ---")
    for response in responses:
        question_id = response.question.id
        if isCorrectAnswer(response):
            base_points = response.question.mark  # base points from the question
            base_score += base_points  # add base points to base score
            total_score+=base_points
            streak_count+=1
            # apply streak bonuses
            streak_bonus= get_streak_bonus(streak_count, base_points)  
            total_score+= streak_bonus     
            # reset the question counter
            if question_id not in question_position:
                question_position[question_id] = 0  # Ensure tracking starts at zero
            question_position[question_id] += 1 # Increment for every response

            position = question_position[question_id]  # Get the updated position
            #apply speed bonuses
            speed_bonus=get_speed_bonus(position)
            total_score+=speed_bonus
            #question_position[question_id] = position
            print(f"✅ Correct Answer | Base: {base_points} | Streak Bonus: {streak_bonus} | Speed Bonus: {speed_bonus} | Total: {total_score}")
        else: #incorrect answer resets streak
            streak_count=0
    #update the participant's score in the database ie without the added bonuses in order to use for stats page later
    #RoomParticipant.objects.filter(user=user, room=room).update(score=base_score)    
    return total_score

def get_leaderboard(room):
    if not room:
        return []

    participants=(RoomParticipant.objects.filter(room=room))
    #calculate scores in bulk
    for participant in participants:
        participant.score = calculate_user_score(participant.user, room)
    #update the score in bulk
    RoomParticipant.objects.bulk_update(participants, ['score'])
    #fetch sorted data 
    leaderboard_data = (
        RoomParticipant.objects.filter(room=room)
        .order_by('-score', 'joined_at')
        .values('user__email_address', 'guest_access__session_id', 'score')
    )
    return[
        {
            "rank":rank,
            "participant": participant["user__email_address"] or f"Guest ({participant['guest_access__session_id'][:8]})",
            "score": participant["score"]
        }
        for rank, participant in enumerate(leaderboard_data, start=1)
    ]

def create_quiz_stats(room):
    Stats.objects.create(
        room=room,
        quiz=room.quiz
    )
    questions = getAllQuestions(room.quiz)
    for question in questions:
        QuestionStats.objects.create(
            room=room,
            question_type=ContentType.objects.get_for_model(question),
            question_id=question.id,
        )

def get_response_model_class(question_type):
    response_model_mapping = {
        'integerinputquestion': IntegerInputResponse,
        'truefalsequestion': TrueFalseResponse,
        'textinputquestion': TextInputResponse,
        'decimalinputquestion': DecimalInputResponse,
        'multiplechoicequestion': MultipleChoiceResponse,
        'numericalrangequestion': NumericalRangeResponse,
        'sortingquestion': SortingResponse,
    }
    response_model = response_model_mapping.get(question_type.model)
    if not response_model:
        raise ValueError("Unknown Response model")
    return response_model


def get_all_responses(room, question):
    question_type=ContentType.objects.get_for_model(question)
    responses = get_response_model_class(question_type).objects.filter(room=room, question=question)
    return responses


