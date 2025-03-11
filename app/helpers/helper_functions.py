from app.models import Quiz, IntegerInputQuestion, Response,TrueFalseQuestion, NumericalRangeResponse, RoomParticipant


def getAllQuestions(quiz):
    if isinstance(quiz, Quiz):
        questions_int = list(IntegerInputQuestion.objects.filter(quiz=quiz))
        questions_tf = list(TrueFalseQuestion.objects.filter(quiz=quiz))
        return questions_int + questions_tf
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

def calculate_user_score(user,room):
    if not user or not room:
        return 0
    #get all the responses for the specific user for a particular room ordered by time
    responses=Response.objects.filter(player=user,room=room).order_by('timestamp')

    base_score=0 # base score ie without bonuses
    score=0 #score including bonuses 
    streak_count=0 # streak tracker
    question_counter={} # stores counters for each question

    for response in responses:
        question_id = response.question.id

        if isCorrectAnswer(response):
            base_points = response.question.mark  # base points from the question
            base_score += base_points  # add base points to base score
            streak_count+=1
    # if streak reaches every 3 -> 1.5x points or if streak reaches every 5-> 2x points 
            score+=base_points
            if streak_count%5==0:
                score+= int(base_points)
            elif streak_count%3==0:
                score+= int(0.5*base_points)
            
    # reset the question counter
            if question_id not in question_counter:
                question_counter[question_id] = 1  # first correct answer for this question
            else:
                question_counter[question_id] += 1  # increment counter for this question

    #points based on timestamp ie first one to answer gets +3 , 2,3,4,5 get +2 and 6,7,8,9,10 get +1 additionally
            position = question_counter[question_id] #get position for this correct response
            if position==1:
                score+=3
            elif 2<=position<=5:
                score+=2
            elif 6<=position<=10:
                score+=1
        else: #incorrect answer resets streak
            streak_count=0

    #update the participant's score in the database ie without the added bonuses in order to use for stats page later
    RoomParticipant.objects.filter(user=user, room=room).update(score=base_score)    
    return score

def get_leaderboard(room):
    if not room:
        return []

    participants=(RoomParticipant.objects.filter(room=room))
    
    for participant in participants:
        calculate_user_score(participant.user, room)

    participants = (
        participants.order_by('-score', 'joined_at')
        .select_related('user', 'guest_access')
        .values('user__email_address', 'guest_access__session_id', 'score')
    )
    leaderboard = []
    #append leaderboard with rank, participant and score
    for rank, participant in enumerate(participants,start=1):
        participant_name = (
            participant['user__email_address']
            if participant['user__email_address']
            else f"Guest ({participant['guest_access__session_id'][:8]})"
        )
        leaderboard.append({
            "rank":rank,
            "participant": participant_name,
            'score':participant['score']
        })
    return leaderboard

