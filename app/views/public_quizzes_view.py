from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect,render, get_object_or_404
from app.helpers.decorators import is_student, is_tutor, redirect_unauthenticated_to_homepage

def public_quizzes_view(request):
    return render(request, 'tutor/public_quizzes.html', {})
