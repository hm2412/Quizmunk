from django.shortcuts import redirect,render, get_object_or_404
from app.forms import QuizForm
from app.models.quiz import Quiz, IntegerInputQuestion, TrueFalseQuestion, Question, TextInputQuestion, MultipleChoiceQuestion, DecimalInputQuestion, NumericalRangeQuestion
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from app.helpers.decorators import is_tutor, redirect_unauthenticated_to_homepage
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from app.models.room import Room, RoomParticipant
from app.question_registry import QUESTION_FORMS, QUESTION_MODELS
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
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


def teacher_live_quiz_view(request, quiz_id):
    quiz = Quiz.objects.filter(id=quiz_id).first()

    if not quiz:
        # Show a message instead of crashing
        return render(request, "tutor/live_quiz.html", {
            "quiz": {"id": quiz_id, "title": "Sample Quiz (Not Found)"},
            "error_message": "Quiz not found. Showing sample questions."
        })

    return render(request, "tutor/live_quiz.html", {"quiz": quiz})


# def start_quiz(request, quiz_id):
#     quiz = get_object_or_404(Quiz, id=quiz_id)
#     first_question = quiz.questions.first()

#     if first_question:
#         return render(request, "partials/current_question.html", {"question": first_question})

#     return JsonResponse({"message": "No questions available"}, status=404)


# def next_question(request, quiz_id):
#     quiz = get_object_or_404(Quiz, id=quiz_id)
#     current_question_id = request.POST.get("current_question_id")

#     if current_question_id:
#         current_question = get_object_or_404(Question, id=current_question_id)
#         next_question = quiz.questions.filter(id__gt=current_question.id).first()
#     else:
#         next_question = quiz.questions.first()

#     if next_question:
#         return render(request, "partials/current_question.html", {"question": next_question})

#     return JsonResponse({"message": "No more questions"}, status=200)

def start_quiz(request, join_code):
    room = Room.objects.get(join_code=join_code)
    room.is_quiz_active = True
    room.current_question_index = 0
    room.save()

    first_question = room.get_current_question()
    answer = get_correct_answer(first_question)
    return JsonResponse({
        'question': first_question.question_text,
        'answer': answer,
        'question_number': 1,
        'total_questions': room.quiz.questions.count()
    })

# def next_question(request, join_code):
#     room = Room.objects.get(join_code=join_code)
#     next_q = room.next_question()
#     answer = get_correct_answer(next_q)

#     if next_q:
#         return JsonResponse({
#             'question': next_q.question_text,
#             'answer': answer,  # Handle different question types
#             'question_number': room.current_question_index + 1,
#             'total_questions': room.quiz.questions.count()
#         })
#     return JsonResponse({'message': 'No more questions'}, status=404)

def next_question(request, join_code):
    room = get_object_or_404(Room, join_code=join_code)
    current_q = room.get_current_question()

    if current_q:
        # Broadcast to WebSocket group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"live_quiz_{join_code}",
            {
                "type": "send.question_update",
                "question": current_q.question_text,
                "answer": current_q.get_correct_answer(),
                "question_number": room.current_question_index + 1
            }
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'quiz_complete'}, status=400)


def end_quiz(request, quiz_id):
    return JsonResponse({"message": "Quiz ended!"})


def get_live_responses(request, quiz_id):
    return JsonResponse({"responses": ["Student A: Answer 1", "Student B: Answer 2"]})

def get_correct_answer(question):
    if isinstance(question, IntegerInputQuestion):
        return question.correct_answer
    elif isinstance(question, TrueFalseQuestion):
        return question.correct_answer
    elif isinstance(question, TextInputQuestion):
        return question.correct_answer
    # Add more elif blocks for other question types
    return None

def tutor_live_quiz(request, join_code):
    """View for the tutor to conduct a live quiz"""
    room = get_object_or_404(Room, join_code=join_code)

    # Get participants excluding tutors
    participants = RoomParticipant.objects.filter(room=room).exclude(user__role="tutor")
    participant_count = participants.count()

    # If the quiz hasn't started, make sure it's ready
    if not room.is_quiz_active:
        room.current_question_index = 0
        room.save()

    context = {
        'room': room,
        'quiz': room.quiz,
        'join_code': join_code,
        'participants': participants,
        'participant_count': participant_count,
    }

    return render(request, 'tutor/live_quiz.html', context)