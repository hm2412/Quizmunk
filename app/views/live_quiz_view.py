from django.shortcuts import redirect,render, get_object_or_404
from app.models import Quiz, IntegerInputQuestion, TrueFalseQuestion
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
def tutor_live_quiz(request):
    return render(request, 'tutor/live_quiz.html')
