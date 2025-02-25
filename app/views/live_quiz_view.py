from django.shortcuts import redirect,render, get_object_or_404
from app.models import Quiz, IntegerInputQuestion, TrueFalseQuestion, Room, RoomParticipant, GuestAccess
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from app.helpers.decorators import is_tutor

@is_tutor
def tutor_live_quiz(request, join_code):
    room = get_object_or_404(Room, join_code=join_code)
    participants = RoomParticipant.objects.filter(room=room)
    participantNumber = participants.count()

    context = {
        'room': room,
        'join_code': join_code,
        'participants': participants,
        'participant_number': participantNumber,
    }
    return render(request, 'tutor/live_quiz.html', context)
