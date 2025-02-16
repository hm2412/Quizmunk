from django.shortcuts import redirect,render, get_object_or_404
from app.forms import QuizForm, IntegerInputQuestionForm, TrueFalseQuestionForm
from app.models import Quiz, IntegerInputQuestion, TrueFalseQuestion, Question
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from app.helpers.decorators import is_tutor, redirect_unauthenticated_to_homepage
from django.views.decorators.http import require_POST

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


def edit_quiz_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    questions_int = list(IntegerInputQuestion.objects.filter(quiz=quiz))
    questions_tf = list(TrueFalseQuestion.objects.filter(quiz=quiz))
    questions = questions_int + questions_tf
    questions.sort(key=lambda q: (q.number if q.number is not None else float('inf')))
    
    if request.method == 'POST':
        if 'integer' in request.POST:
            int_form = IntegerInputQuestionForm(request.POST)
            tf_form = TrueFalseQuestionForm() # Empty form to avoid errors in the template
            if int_form.is_valid():
                question = int_form.save(commit=False)
                question.quiz = quiz
                question.save()
                print(" Integer question saved successfully!")
                return redirect('edit_quiz', quiz_id=quiz.id)
            else:
                print(" Integer form validation failed:", int_form.errors)
        elif 'true_false' in request.POST:
            tf_form = TrueFalseQuestionForm(request.POST)
            int_form= IntegerInputQuestionForm() # Empty form to avoid errors in the template
            if tf_form.is_valid():
                question = tf_form.save(commit=False)
                question.quiz = quiz
                question.save()
                print("True/False question saved successfully!")
                return redirect('edit_quiz', quiz_id=quiz.id)
            else:
                print("True/False form validation failed:", tf_form.errors)
    else:
        int_form = IntegerInputQuestionForm(initial={'quizID': str(quiz.id)})
        tf_form = TrueFalseQuestionForm(initial={'quizID': str(quiz.id)})
    
    return render(request, 'tutor/edit_quiz.html', {
        'quiz': quiz,
        'int_form': int_form,
        'tf_form': tf_form,
        'questions': questions,
    })


def delete_question_view(request, question_id):
    try:
        question = IntegerInputQuestion.objects.get(pk=question_id)
    except IntegerInputQuestion.DoesNotExist:
        try:
            question = TrueFalseQuestion.objects.get(pk=question_id)
        except TrueFalseQuestion.DoesNotExist:
            return HttpResponse("Question not found",status=404)
    quiz_id = question.quiz.id
    question.delete()
    return redirect('edit_quiz', quiz_id=quiz_id)


def get_question_view(request, quiz_id):
    question_id = request.GET.get('question_id')
    if not question_id:
        return JsonResponse({"error": "Question ID is required"}, status=400)
    
    try:
        question = IntegerInputQuestion.objects.get(pk=question_id)
        question_type = "integer"
    except IntegerInputQuestion.DoesNotExist:
        try:
            question= TrueFalseQuestion.objects.get(pk=question_id)
            question_type = "true_false"
        except TrueFalseQuestion.DoesNotExist:
            return JsonResponse({"error":"Question not found"}, status=404)
    data = {
        "id": question.id,
        "question_type": question_type,
        "question_text": question.question_text,
        "number": question.number,
        "time": question.time,
        "quizID": question.quiz.id,
    }
    if question_type == "integer":
        data["mark"] = question.mark
        data["correct_answer"] = question.correct_answer
    else:
        data["mark"] = question.mark
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