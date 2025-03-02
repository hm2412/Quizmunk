from django.shortcuts import redirect,render, get_object_or_404
from app.models import Quiz, RoomParticipant, Room
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from app.helpers.decorators import is_tutor
from django.views.decorators.csrf import csrf_exempt

QUESTIONS = [
    {"question": "What is the capital of France?", "answer": "Paris"},
    {"question": "What is 2 + 2?", "answer": "4"},
    {"question": "What is the largest ocean?", "answer": "Pacific Ocean"},
]

quiz_state = {"current_question": -1, "quiz_started": False}


@is_tutor
def tutor_live_quiz(request, join_code):
    room = get_object_or_404(Room, join_code=join_code)
    participants = RoomParticipant.objects.filter(room=room)
    leaders = RoomParticipant.objects.filter(room=room).order_by('-score')[:10]
    participantNumber = participants.count()

    context = {
        'room': room,
        'join_code': join_code,
        'participants': participants,
        'leaders': leaders,
        'participant_number': participantNumber,
    }
    return render(request, 'tutor/live_quiz.html', context)

def start_quiz(request):
    if request.method == "POST":
        quiz_state["current_question"] = 0
        quiz_state["quiz_started"] = True
        return JsonResponse({"message": "Quiz started!"})
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def next_question(request):
    if request.method == "POST":
        if quiz_state["current_question"] < len(QUESTIONS) - 1:
            quiz_state["current_question"] += 1
            question_data = QUESTIONS[quiz_state["current_question"]]
            return JsonResponse({
                "question_number": quiz_state["current_question"] + 1,
                "question": question_data["question"],
                "answer": question_data["answer"]
            })
        else:
            return JsonResponse({"message": "No more questions!"})
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def end_quiz(request):
    if request.method == "POST":
        quiz_state["current_question"] = -1
        quiz_state["quiz_started"] = False
        return JsonResponse({"message": "Quiz ended!"})
    return JsonResponse({"error": "Invalid request"}, status=400)




def student_live_quiz(request, room_code):
    room = get_object_or_404(Room, join_code=room_code)
    return render(request, 'student/student_live_quiz.html', {'room': room})
