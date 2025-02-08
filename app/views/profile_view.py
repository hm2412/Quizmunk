from django.shortcuts import render
from app.helpers.decorators import is_student, is_tutor, redirect_unauthenticated_to_homepage

@redirect_unauthenticated_to_homepage
@is_student
def student_profile(request):
    return render(request, 'student/student_profile.html', {'user': request.user})

@redirect_unauthenticated_to_homepage
@is_tutor
def tutor_profile(request):
    return render(request, 'tutor/tutor_profile.html', {'user': request.user})
