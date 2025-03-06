from django.shortcuts import redirect,render, get_object_or_404
from app.forms import QuizForm
from app.models.quiz import Quiz, IntegerInputQuestion, TrueFalseQuestion, Question, TextInputQuestion, MultipleChoiceQuestion, DecimalInputQuestion, NumericalRangeQuestion
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from app.helpers.decorators import is_tutor, redirect_unauthenticated_to_homepage
from django.views.decorators.http import require_POST
from app.question_registry import QUESTION_FORMS, QUESTION_MODELS

@redirect_unauthenticated_to_homepage
@is_tutor
def create_quiz_view(request):
    form = QuizForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.tutor = request.user
            quiz.save()
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Redirect'] = reverse('edit_quiz', kwargs={'quiz_id': quiz.id})
                return response
            else:
                return redirect('edit_quiz', quiz_id=quiz.id)
        else:
            return render(request, 'tutor/create_quiz_form.html', {'form': form}, status=400)
    
    return render(request, 'tutor/create_quiz_form.html', {'form': form})


@redirect_unauthenticated_to_homepage
@is_tutor
def edit_quiz_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    #if new types are added add them here
    questions_int = list(IntegerInputQuestion.objects.filter(quiz=quiz))
    questions_tf = list(TrueFalseQuestion.objects.filter(quiz=quiz))
    questions_ti = list(TextInputQuestion.objects.filter(quiz=quiz))
    questions_mc = list(MultipleChoiceQuestion.objects.filter(quiz=quiz))
    questions_dc = list(DecimalInputQuestion.objects.filter(quiz=quiz))
    questions_nr = list(NumericalRangeQuestion.objects.filter(quiz=quiz))
    questions = questions_int + questions_tf + questions_ti + questions_mc + questions_dc + questions_nr
    questions.sort(key=lambda q: (q.position if q.position is not None else float('inf')))

    form_type = None
    form = None
    
    if request.method == 'POST':
        for key in QUESTION_FORMS:
            if key in request.POST:
                form_type = key
                break
        if form_type:
            form_class = QUESTION_FORMS.get(form_type)
            form = form_class(request.POST, request.FILES)
            if form.is_valid():
                question = form.save(commit=False)
                question.quiz = quiz
                question.save()
                print("Question saved successfully!")
                return redirect('edit_quiz', quiz_id=quiz.id)
            else:
                print("Form validation failed:", form.errors)
                question_forms = {}
                for key, form_class in QUESTION_FORMS.items():
                    if key == form_type:
                        question_forms[key] = form
                    else:
                        question_forms[key] = form_class(initial={'quizID': str(quiz.id)})
                return render(request, 'tutor/edit_quiz.html', {
                    'quiz': quiz,
                    'form': form,
                    'questions': questions,
                    'question_forms': question_forms,
                })

    else:
        # Initialize form based on the selected form type
        for key in QUESTION_FORMS:
            if key in request.GET:
                form_type = key
                break

        if form_type:
            form_class = QUESTION_FORMS.get(form_type)
            form = form_class(initial={'quizID': str(quiz.id)})

    #makes loading the forms easier 
    question_forms = {}
    for key, form_class in QUESTION_FORMS.items():
        question_forms[key] = form_class(initial={'quizID': str(quiz.id)})

    return render(request, 'tutor/edit_quiz.html', {
        'quiz': quiz,
        'form': form,
        'questions': questions,
        'question_forms': question_forms,
    })


@redirect_unauthenticated_to_homepage
@is_tutor
def delete_question_view(request, question_id):
    question = None
    for key, model in QUESTION_MODELS.items():
        try:
            question = model.objects.get(pk=question_id)
            break
        except model.DoesNotExist:
            continue

    if not question:
        return HttpResponse("Question not found", status=404)
    
    quiz_id = question.quiz.id
    question.delete()
    return redirect('edit_quiz', quiz_id=quiz_id)


@redirect_unauthenticated_to_homepage
@is_tutor
def get_question_view(request, quiz_id):
    question_id = request.GET.get('question_id')
    if not question_id:
        return JsonResponse({"error": "Question ID is required"}, status=400)
    
    question = None
    question_type = None
    for key, model in QUESTION_MODELS.items():
        try:
            question = model.objects.get(pk=question_id)
            question_type = key
            break
        except model.DoesNotExist:
            continue

    if not question:
        return JsonResponse({"error": "Question not found"}, status=404)

    data = {
        "id": question.id,
        "question_type": question_type,
        "question_text": question.question_text,
        "position": question.position,
        "time": question.time,
        "quizID": question.quiz.id,
        "mark": question.mark,
        "image": question.image.url if hasattr(question, 'image') and question.image else "",
    }

    #add more types here with their uniqe fields
    if question_type == "integer" or question_type == 'text' or question_type == "decimal":
        data["correct_answer"] = question.correct_answer
    elif question_type == "multiple_choice":
        data["options"] = question.options
        data["correct_option"] = question.correct_option
    elif question_type == "numerical_range":
        data["min_value"] = question.min_value
        data["max_value"] = question.max_value
    else:
        data["is_correct"] = question.is_correct
    return JsonResponse(data)


#this is for the your Quizzes page

@redirect_unauthenticated_to_homepage
@is_tutor
def your_quizzes_view(request):
    """show the drafts created by the tutor"""
    drafts = Quiz.objects.filter(tutor=request.user).order_by("-id")
    context = {'drafts':drafts}
    return render(request, 'tutor/your_quizzes.html', context)


@redirect_unauthenticated_to_homepage
@is_tutor
@require_POST
def delete_quiz_view(request, quiz_id):
    """deletes a quiz that belongs to the tutor"""
    print(f"Delete request received for quiz ID: {quiz_id}") 
    quiz = get_object_or_404(Quiz, id=quiz_id, tutor=request.user)
    print(f"Deleting quiz: {quiz}") 
    quiz.delete()
    if request.headers.get('HX-Request'):
            print("HTMX request detected. Returning 204 No Content.")
            return HttpResponse(status=204)
    print("Standard request. Redirecting to 'your_quizzes'.")
    return redirect('your_quizzes')


def teacher_live_quiz_view(request, quiz_id):
    quiz = Quiz.objects.filter(id=quiz_id).first()

    if not quiz:
        # Show a message instead of crashing
        return render(request, "tutor/live_quiz.html", {
            "quiz": {"id": quiz_id, "title": "Sample Quiz (Not Found)"},
            "error_message": "Quiz not found. Showing sample questions."
        })

    return render(request, "tutor/live_quiz.html", {"quiz": quiz})


def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    first_question = quiz.questions.first()

    if first_question:
        return render(request, "partials/current_question.html", {"question": first_question})
    
    return JsonResponse({"message": "No questions available"}, status=404)


def next_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    current_question_id = request.POST.get("current_question_id")

    if current_question_id:
        current_question = get_object_or_404(Question, id=current_question_id)
        next_question = quiz.questions.filter(id__gt=current_question.id).first()
    else:
        next_question = quiz.questions.first()

    if next_question:
        return render(request, "partials/current_question.html", {"question": next_question})

    return JsonResponse({"message": "No more questions"}, status=200)


def end_quiz(request, quiz_id):
    return JsonResponse({"message": "Quiz ended!"})


def get_live_responses(request, quiz_id):
    return JsonResponse({"responses": ["Student A: Answer 1", "Student B: Answer 2"]})