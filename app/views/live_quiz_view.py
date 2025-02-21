from django.shortcuts import render, get_object_or_404
from app.models import Quiz

def live_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    return render(request, 'live_quiz.html', {'quiz': quiz})
