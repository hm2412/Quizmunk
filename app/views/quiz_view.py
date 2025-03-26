import json
from django.shortcuts import redirect,render, get_object_or_404
from app.forms import QuizForm
from app.models.quiz import Quiz
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from app.helpers.decorators import is_tutor, redirect_unauthenticated_to_homepage
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from app.question_registry import QUESTION_FORMS, QUESTION_MODELS
from app.helpers.helper_functions import getAllQuestions
from django.contrib import messages

@redirect_unauthenticated_to_homepage
@is_tutor
def create_quiz_view(request):
    form = QuizForm(request.POST or None, request.FILES or None)
    
    if request.method == 'POST':
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.tutor = request.user

            if 'quiz_img' in request.FILES:
                quiz.quiz_img = request.FILES['quiz_img']

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
    questions = getAllQuestions(quiz=quiz)
    questions.sort(key=lambda q: (q.position if q.position is not None else float('inf')))
    form_type = None
    form = None

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_settings':
            # Handle quiz settings update
            quiz.name = request.POST.get('name', quiz.name)
            quiz.subject = request.POST.get('subject', quiz.subject)
            quiz.is_public = request.POST.get('is_public') == 'on'
            quiz.save()
            messages.success(request, 'Quiz settings updated successfully')
            return redirect('your_quizzes')
        hx_request = request.headers.get('HX-Request')
        for key in QUESTION_FORMS:
            if key in request.POST:
                form_type = key
                break

        if form_type:
            question_id = request.POST.get("question_id")
            form_class = QUESTION_FORMS.get(form_type)
            if question_id:
                model_class = QUESTION_MODELS.get(form_type)
                instance = get_object_or_404(model_class, pk=question_id, quiz=quiz)
                form = form_class(request.POST, request.FILES, instance=instance)
            else:
                form = form_class(request.POST, request.FILES)

            if form.is_valid():
                question = form.save(commit=False)
                question.quiz = quiz
                if not question.pk or question.position is None:
                    existing_questions = getAllQuestions(quiz=quiz)
                    max_position = max((q.position for q in existing_questions if q.position is not None), default=0)
                    question.position = max_position + 1
                question.save()
                if hx_request:
                    response = HttpResponse()
                    response['HX-Redirect'] = reverse('edit_quiz', kwargs={'quiz_id': quiz.id})
                    return response
                else:
                    return redirect('edit_quiz', quiz_id=quiz.id)
            else:
                if hx_request:
                    return render(request, 'partials/question_editor.html', {
                        'quiz': quiz,
                        'form': form,
                        'form_type': form_type
                    })
                else:
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
        return redirect('edit_quiz', quiz_id=quiz.id)
    else:
        for key in QUESTION_FORMS:
            if key in request.GET:
                form_type = key
                break

        if form_type:
            form_class = QUESTION_FORMS.get(form_type)
            form = form_class(initial={'quizID': str(quiz.id)})

    question_forms = {}
    for key, form_class in QUESTION_FORMS.items():
        question_forms[key] = form_class(initial={'quizID': str(quiz.id)})

    questions = getAllQuestions(quiz=quiz)
    questions.sort(key=lambda q: (q.position if q.position is not None else float('inf')))

    return render(request, 'tutor/edit_quiz.html', {
        'quiz': quiz,
        'form': form,
        'questions': questions,
        'question_forms': question_forms,
    })


@redirect_unauthenticated_to_homepage
@is_tutor
def delete_question_view(request, question_type, question_id):
    model = QUESTION_MODELS.get(question_type)
    if not model:
        return JsonResponse({"error": "Invalid question type"}, status=400)
    
    try:
        question = model.objects.get(pk=question_id)
    except model.DoesNotExist:
        return JsonResponse({"error": "Question not found"}, status=404)
    question.delete()
    return JsonResponse({"status": "success"})


@redirect_unauthenticated_to_homepage
@is_tutor
def delete_question_image_view(request, question_id):
    question = None
    for key, model in QUESTION_MODELS.items():
        try:
            question = model.objects.get(pk=question_id)
            break
        except model.DoesNotExist:
            continue

    if not question:
        return JsonResponse({"error": "Question not found"}, status=404)
    
    if question.image:
        if default_storage.exists(question.image.name):
            default_storage.delete(question.image.name)
        question.image = None
        question.save()
    return JsonResponse({"status": "success"})


@redirect_unauthenticated_to_homepage
@is_tutor
def update_question_order(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)
    try:
        quiz_id = request.POST.get("quiz_id")
        if not quiz_id:
            return JsonResponse({"status": "error", "message": "Quiz ID is required"}, status=400)
        data = json.loads(request.POST.get("order", "[]"))
        for index, identifier in enumerate(data, start=1):
            try:
                question_type, question_id = identifier.split("-", 1)
            except ValueError:
                return JsonResponse({"status": "error", "message": "Invalid identifier format"}, status=400)

            model = QUESTION_MODELS.get(question_type)
            if not model:
                return JsonResponse({"status": "error", "message": f"Invalid question type: {question_type}"}, status=400)

            try:
                question = model.objects.get(id=question_id, quiz_id=quiz_id)
            except model.DoesNotExist:
                return JsonResponse({"status": "error", "message": f"Question with ID {question_id} not found in this quiz"}, status=404)

            question.position = index
            question.save()

        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@redirect_unauthenticated_to_homepage
@is_tutor
def get_question_view(request, quiz_id):
    question_id = request.GET.get('question_id')
    question_type = request.GET.get('question_type') 
    if not question_id or not question_type:
        return JsonResponse({"error": "Question ID and type are required"}, status=400)
    
    model = QUESTION_MODELS.get(question_type)
    if not model:
        return JsonResponse({"error": "Invalid question type"}, status=400)
    
    try:
        question = model.objects.get(pk=question_id, quiz_id=quiz_id)
    except model.DoesNotExist:
        return JsonResponse({"error": "Question not found"}, status=404)
    
    data = {
        "id": question.id,
        "question_type": question_type,
        "question_text": question.question_text,
        "position": question.position,
        "time": question.time,
        "quizID": question.quiz.id,
        "mark": question.mark,
        "image": question.image.url if question.image else "",
    }

    #add more types here with their unique fields
    if question_type == "multiple_choice":
        data["options"] = question.options
        data["correct_answer"] = question.correct_answer
    elif question_type == "numerical_range":
        data["min_value"] = question.min_value
        data["max_value"] = question.max_value
    else:
        data["correct_answer"] = question.correct_answer
    return JsonResponse(data)


#this is for the your Quizzes page


@redirect_unauthenticated_to_homepage
@is_tutor
def your_quizzes_view(request):
    drafts = Quiz.objects.filter(tutor=request.user).order_by("-id")
    return render(request, 'tutor/your_quizzes.html', {'drafts': drafts})


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
