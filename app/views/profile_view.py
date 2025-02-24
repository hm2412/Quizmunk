from django.shortcuts import render
from app.helpers.decorators import is_student, is_tutor, redirect_unauthenticated_to_homepage
from django.views.decorators.cache import never_cache

@redirect_unauthenticated_to_homepage
@is_student
@never_cache
def student_profile(request):
    return render(request, 'student/student_profile.html', {'user': request.user})

@redirect_unauthenticated_to_homepage
@is_tutor
@never_cache
def tutor_profile(request):
    return render(request, 'tutor/tutor_profile.html', {'user': request.user})
