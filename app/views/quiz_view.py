from django.shortcuts import redirect,render, get_object_or_404
from app.forms import QuizForm, IntegerInputQuestionForm, TrueFalseQuestionForm
from app.models import Quiz, IntegerInputQuestion, TrueFalseQuestion
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
def create_quiz_view(request):
    form = QuizForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            quiz = form.save()
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
    
    questions_int = list(IntegerInputQuestion.objects.filter(quizID=str(quiz.id)))
    questions_tf = list(TrueFalseQuestion.objects.filter(quizID=str(quiz.id)))
    questions = questions_int + questions_tf
    questions.sort(key=lambda q: (q.number if q.number is not None else float('inf')))
    
    if request.method == 'POST':
        if 'integer' in request.POST:
            int_form = IntegerInputQuestionForm(request.POST)
            tf_form = TrueFalseQuestionForm() # Empty form to avoid errors in the template
            if int_form.is_valid():
                question = int_form.save(commit=False)
                question.quizID = quiz.id
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
                question.quizID = quiz.id
                question.save()
                print("True/False question saved successfully!")
                return redirect('edit_quiz', quiz_id=quiz.id)
            else:
                print("True/False form validation failed:", tf_form.errors)
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
        try:
            question = TrueFalseQuestion.objects.get(pk=question_id)
        except TrueFalseQuestion.DoesNotExist:
            return HttpResponse("Question not found",status=404)
    quiz_id = int(question.quizID)
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
        "quizID": question.quizID,
    }
    if question_type == "integer":
        data["mark"] = question.mark
        data["correct_answer"] = question.correct_answer
    else:
        data["mark"] = question.mark
        data["is_correct"] = question.is_correct
    return JsonResponse(data)