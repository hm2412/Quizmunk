from django.shortcuts import redirect,render, get_object_or_404
from app.models import Quiz, RoomParticipant, Room
from django.http import HttpResponse, JsonResponse
from django.urls import reverse

def tutor_live_quiz(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    leaders = RoomParticipant.objects.filter(room=room).order_by('-score')[:10]  

    return render(request, 'tutor/live_quiz.html', {'leaders': leaders})
