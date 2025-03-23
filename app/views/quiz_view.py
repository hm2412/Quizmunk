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
        # Debug: print whether the request was made via HTMX.
        hx_request = request.headers.get('HX-Request')
        print("HX-Request header:", hx_request)

        # Identify which question form is being submitted
        for key in QUESTION_FORMS:
            if key in request.POST:
                form_type = key
                break

        if form_type:
            question_id = request.POST.get("question_id")
            form_class = QUESTION_FORMS.get(form_type)
            if question_id:
                model_class = QUESTION_MODELS.get(form_type)
                instance = get_object_or_404(model_class, pk=question_id)
                form = form_class(request.POST, request.FILES, instance=instance)
            else:
                form = form_class(request.POST, request.FILES)

            if form.is_valid():
                question = form.save(commit=False)
                question.quiz = quiz
                question.save()
                print("Question saved successfully!")
                if hx_request:
                    # Use HX-Redirect to force a full page refresh so saved questions are updated.
                    response = HttpResponse()
                    response['HX-Redirect'] = reverse('edit_quiz', kwargs={'quiz_id': quiz.id})
                    return response
                else:
                    return redirect('edit_quiz', quiz_id=quiz.id)
            else:
                print("Form validation failed:", form.errors)
                if hx_request:
                    # Return the partial with the form (including errors)
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

        # Handle quiz image update if provided.
        if 'quiz_img' in request.FILES:
            quiz.quiz_img = request.FILES['quiz_img']
            quiz.save()

        return redirect('edit_quiz', quiz_id=quiz.id)
    else:
        # On GET, check if a specific form type is requested.
        for key in QUESTION_FORMS:
            if key in request.GET:
                form_type = key
                break

        if form_type:
            form_class = QUESTION_FORMS.get(form_type)
            form = form_class(initial={'quizID': str(quiz.id)})

    # Prepare all hidden question form templates
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
def delete_question_image_view(request, question_id):
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
    if question.image:
        if default_storage.exists(question.image.name):
            default_storage.delete(question.image.name)
        question.image = None
        question.save()
    return redirect('edit_quiz', quiz_id=quiz_id)


@redirect_unauthenticated_to_homepage
@is_tutor
def update_question_order(request):
    import json

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

    try:
        print("Received request to update order")  # Debugging line
        data = json.loads(request.POST.get("order", "[]"))
        print("Received order:", data)  # Debugging line

        for index, question_id in enumerate(data, start=1):
            question = None
            for key, model in QUESTION_MODELS.items():
                try:
                    question = model.objects.get(id=question_id)
                    break
                except model.DoesNotExist:
                    continue

            if not question:
                return JsonResponse({"status": "error", "message": f"Question with ID {question_id} not found"}, status=404)

            question.position = index
            question.save()

        return JsonResponse({"status": "success"})

    except Exception as e:
        print(f"Error updating order: {e}")  # Debugging line
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@redirect_unauthenticated_to_homepage
@is_tutor
def get_question_view(request, quiz_id):
    question_id = request.GET.get('question_id')
    question_type = request.GET.get('question_type')  # new parameter
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