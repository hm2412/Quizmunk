from django.shortcuts import render
from quizsite.app.helpers.decorators import is_student, is_tutor, redirect_unauthenticated_to_homepage

@redirect_unauthenticated_to_homepage
@is_student
def student_dashboard(request):
    return render(request, 'student_dashboard.html')

@redirect_unauthenticated_to_homepage
@is_tutor
def tutor_dashboard(request):
    return render(request, 'tutor_dashboard.html')
