from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect,render, get_object_or_404
from app.models import Quiz
from django.contrib.contenttypes.models import ContentType
from app.helpers.decorators import is_student, is_tutor, redirect_unauthenticated_to_homepage
from app.helpers.helper_functions import getAllQuestions
from app.question_registry import QUESTION_MODELS

@redirect_unauthenticated_to_homepage
@is_tutor
def public_quizzes_view(request):
    quizzes = Quiz.objects.filter(is_public=True).exclude(tutor=request.user).order_by("-id")
    return render(request, 'tutor/public_quizzes.html', {'quizzes':quizzes})

@redirect_unauthenticated_to_homepage
@is_tutor
def save_public_quiz_view(request, quiz_id):
    original_quiz = get_object_or_404(Quiz, id=quiz_id, is_public=True)
    new_quiz = Quiz.objects.create(
        name=f"Copy of {original_quiz.name}",
        subject=original_quiz.subject,
        difficulty=original_quiz.difficulty,
        type=original_quiz.type,
        tutor=request.user
    )
    new_quiz.save()
    questions = original_quiz.get_all_questions()
    for question in questions:
        question.pk = None
        question.quiz = new_quiz
        question.save()

    return redirect('edit_quiz', new_quiz.id)

@is_tutor
def quiz_preview_modal_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, is_public=True)
    questions = quiz.get_all_questions()
    # for question in questions:
    #     # if question.items:
    #     #     question.items = question.get_items()

    return render(request, 'partials/_quiz_preview_modal.html', {
        'quiz': quiz,
        'questions': questions
    })
