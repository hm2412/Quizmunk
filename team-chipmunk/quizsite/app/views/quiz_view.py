from django.shortcuts import redirect,render, get_object_or_404
from quizsite.app.forms import QuizForm, IntegerInputQuestionForm, TrueFalseQuestionForm
from quizsite.app.models import Quiz, Question
def create_quiz_view(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('edit_quiz',quiz_id=form.instance.ID)
    else:
        form = QuizForm()
    return render(request, 'create_quiz.html',{'form':form})

def edit_quiz_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, ID=quiz_id)
    if request.method == 'POST':
        if 'integer' in request.POST:  
            int_form = IntegerInputQuestionForm(request.POST)
            if int_form.is_valid():
                int_form.save()
        elif 'true_false' in request.POST:
            tf_form = TrueFalseQuestionForm(request.POST)
            if tf_form.is_valid():
                tf_form.save()
    
    else:
        int_form = IntegerInputQuestionForm(initial={'quizID': quiz_id})
        tf_form = TrueFalseQuestionForm(initial={'quizID': quiz_id})

    return render(request, 'edit_quiz.html',{
        'quiz':quiz,
        'int_form':int_form,
        'tf_form':tf_form
    })

def delete_question_view(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.delete()
    return redirect('edit_quiz', quiz_id=question.quizID)