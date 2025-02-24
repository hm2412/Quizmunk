from django.shortcuts import redirect,render, get_object_or_404
from app.models import Quiz, IntegerInputQuestion, TrueFalseQuestion
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

QUESTIONS = [
    {"question": "What is the capital of France?", "answer": "Paris"},
    {"question": "What is 2 + 2?", "answer": "4"},
    {"question": "What is the largest ocean?", "answer": "Pacific Ocean"},
]

quiz_state = {"current_question": -1, "quiz_started": False}

def tutor_live_quiz(request):
    return render(request, 'tutor/live_quiz.html')

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