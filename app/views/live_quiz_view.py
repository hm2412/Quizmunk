from django.shortcuts import render, get_object_or_404
from app.models import Room

def student_live_quiz(request, room_code):
    room = get_object_or_404(Room, join_code=room_code)
    return render(request, 'student/student_live_quiz.html', {'room': room})
