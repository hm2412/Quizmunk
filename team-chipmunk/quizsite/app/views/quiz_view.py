from django.shortcuts import redirect,render, get_object_or_404
from quizsite.app.forms import QuizForm, IntegerInputQuestionForm, TrueFalseQuestionForm
from quizsite.app.models import Quiz, IntegerInputQuestion, TrueFalseQuestion
from django.http import HttpResponse, JsonResponse
from django.urls import reverse

def create_quiz_view(request):
    form = QuizForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        quiz = form.save()
        if request.headers.get('HX-Request'):
            response = HttpResponse()
            response['HX-Redirect'] = reverse('edit_quiz', kwargs={'quiz_id': quiz.id})
            return response
        else:
            return redirect('edit_quiz', quiz_id=quiz.id)
    
    return render(request, 'partials/create_quiz_form.html', {'form': form})


def edit_quiz_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    questions_int = list(IntegerInputQuestion.objects.filter(quizID=str(quiz.id)))
    questions_tf = list(TrueFalseQuestion.objects.filter(quizID=str(quiz.id)))
    questions = questions_int + questions_tf
    questions.sort(key=lambda q: q.number)
    
    if request.method == 'POST':
        if 'integer' in request.POST:
            int_form = IntegerInputQuestionForm(request.POST)
            if int_form.is_valid():
                int_form.save()
                return redirect('edit_quiz', quiz_id=quiz.id)
            else:
                tf_form = TrueFalseQuestionForm(initial={'quizID': str(quiz.id)})
        elif 'true_false' in request.POST:
            tf_form = TrueFalseQuestionForm(request.POST)
            if tf_form.is_valid():
                tf_form.save()
                return redirect('edit_quiz', quiz_id=quiz.id)
            else:
                int_form = IntegerInputQuestionForm(initial={'quizID': str(quiz.id)})
    else:
        int_form = IntegerInputQuestionForm(initial={'quizID': str(quiz.id)})
        tf_form = TrueFalseQuestionForm(initial={'quizID': str(quiz.id)})
    
    return render(request, 'edit_quiz.html', {
        'quiz': quiz,
        'int_form': int_form,
        'tf_form': tf_form,
        'questions': questions,
    })


def delete_question_view(request, question_id):
    try:
        question = IntegerInputQuestion.objects.get(pk=question_id)
    except IntegerInputQuestion.DoesNotExist:
        question = get_object_or_404(TrueFalseQuestion, pk=question_id)
    quiz_id = int(question.quizID)
    question.delete()
    return redirect('edit_quiz', quiz_id=quiz_id)


def get_question_view(request, quiz_id):
    question_id = request.GET.get('question_id')
    try:
        question = IntegerInputQuestion.objects.get(pk=question_id)
        question_type = "integer"
    except IntegerInputQuestion.DoesNotExist:
        question = get_object_or_404(TrueFalseQuestion, pk=question_id)
        question_type = "true_false"
    data = {
        "id": question.id,
        "question_type": question_type,
        "question_text": question.question_text,
        "number": question.number,
        "time": question.time,
        "quizID": question.quizID,
    }
    if question_type == "integer":
        data["mark"] = question.mark
        data["correct_answer"] = question.correct_answer
    else:
        data["mark"] = question.mark
        data["is_correct"] = question.is_correct
    return JsonResponse(data)