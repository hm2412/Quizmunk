from django.shortcuts import render
from app.helpers.decorators import is_student, is_tutor, redirect_unauthenticated_to_homepage
from app.models import Quiz


@redirect_unauthenticated_to_homepage
@is_student
def student_dashboard(request):
    return render(request, 'student/student_dashboard.html')

@redirect_unauthenticated_to_homepage
@is_tutor
def tutor_dashboard(request):
    quizzes = Quiz.objects.filter(tutor=request.user.id).order_by('-id')[:5]

    return render(request, 'tutor/tutor_dashboard.html', {"quizzes": quizzes})
