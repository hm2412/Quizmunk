from django.shortcuts import render
from app.helpers.decorators import is_student, is_tutor, redirect_unauthenticated_to_homepage
from django.views.decorators.cache import never_cache
from app.models import Quiz, ClassroomStudent, Classroom
from app.helpers.helper_functions import get_student_quiz_history

@redirect_unauthenticated_to_homepage
@is_student
@never_cache
def student_dashboard(request):
    student = request.user
    student_results = get_student_quiz_history(student)
    # Fetch available quizzes from classrooms the student is in
    # 1. Get all classrooms the student is a part of
    classroom_ids = ClassroomStudent.objects.filter(student=student).values_list('classroom_id', flat=True)

    # 2. Get all tutors of those classrooms
    tutor_ids = Classroom.objects.filter(id__in=classroom_ids).values_list('tutor_id', flat=True)

    # 3. Get quizzes created by those tutors
    available_quizzes = Quiz.objects.filter(tutor_id__in=tutor_ids).order_by('-id')

    context = {
        'available_quizzes': available_quizzes,
        'student_results': student_results,
    }
    return render(request, 'student/student_dashboard.html',context)

@redirect_unauthenticated_to_homepage
@is_tutor
@never_cache
def tutor_dashboard(request):
    quizzes = Quiz.objects.filter(tutor=request.user.id).order_by('-id')[:5]

    return render(request, 'tutor/tutor_dashboard.html', {"quizzes": quizzes})
