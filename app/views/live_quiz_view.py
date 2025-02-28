from django.shortcuts import redirect,render, get_object_or_404
from app.models import Quiz, RoomParticipant, Room, Question, IntegerInputQuestion, TrueFalseQuestion, QuizState
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from app.helpers.decorators import is_tutor
from app.helpers.helper_functions import getAllQuestions
from django.views.decorators.csrf import csrf_exempt


'''Student Live Quiz'''
def student_live_quiz(request, room_code):
    room = get_object_or_404(Room, join_code=room_code)
    return render(request, 'student/student_live_quiz.html', {'room': room})


'''Tutor Live Quiz'''
def get_room(join_code):
    return get_object_or_404(Room, join_code=join_code)

@is_tutor
def tutor_live_quiz(request, join_code):
    room = get_room(join_code)
    participants = RoomParticipant.objects.filter(room=room)
    leaders = participants.order_by('-score')[:10]
    participantNumber = participants.count()

    context = {
        'room': room,
        'join_code': join_code,
        'participants': participants,
        'leaders': leaders,
        'participant_number': participantNumber,
    }
    return render(request, 'tutor/live_quiz.html', context)

def start_quiz(request, join_code):
    room = get_room(join_code)
    questions = getAllQuestions(room.quiz)

    if not questions:
        return JsonResponse({"error": "No questions found for this quiz."}, status=400)

    if request.method == "POST":
        quiz_state, created = QuizState.objects.get_or_create(room=room)
        if not created:
            quiz_state.current_question_index = 0
            quiz_state.quiz_started = True
            quiz_state.save()

        return JsonResponse({"message": "Quiz started!"})
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def next_question(request, join_code):

    # Ensure the room exists
    room = get_room(join_code)
    if not room:
        return JsonResponse({"error": "Room not found."}, status=400)

    # Ensure the quiz state exists
    quiz_state = QuizState.objects.filter(room=room).first()
    if not quiz_state:
        return JsonResponse({"error": "Quiz has not started for this room."}, status=400)

    # Ensure the quiz has started
    if not quiz_state.quiz_started:
        return JsonResponse({"error": "Quiz has not started for this room."}, status=400)

    # Process only POST requests
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    # Retrieve questions
    quiz = room.quiz
    questions = getAllQuestions(quiz)

    # Check if there are more questions
    if quiz_state.current_question_index < len(questions):
        current_question = questions[quiz_state.current_question_index]
        quiz_state.current_question_index += 1
        quiz_state.save()
        return JsonResponse({
            "question_number": quiz_state.current_question_index,
            "question": current_question.question_text,  
            # "answer": current_question.correct_answer
        })
    else:
        return JsonResponse({"message": "No more questions!"})




@csrf_exempt
def end_quiz(request, join_code):
    room = get_room(join_code)
    quiz_state = QuizState.objects.filter(room=room).first()
    if request.method == "POST":
        if quiz_state:
            quiz_state.current_question_index = -1
            quiz_state.quiz_started = False
            quiz_state.save()
            return JsonResponse({"message": "Quiz ended!"})
        return JsonResponse({"error": "Quiz not found for this room."}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

