from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from quizsite.app.models import Room, RoomParticipant, GuestAccess

def lobby(request, join_code):
    room = get_object_or_404(Room, join_code=join_code)

    #if not room.quiz:
    #    messages.error(request, 'Invalid code!')
    #    return redirect('join_quiz')

    if request.user.is_authenticated:
        participant, created = RoomParticipant.objects.get_or_create(room=room, user=request.user)
    else:
        guest_session = request.session.session_key
        if not guest_session:
            request.session.save()
            guest_session = request.session.session_key
        guest_access, _ = GuestAccess.objects.get_or_create(session_id=guest_session)
        participant, created = RoomParticipant.objects.get_or_create(room=room, guest_access=guest_access)

    participants = RoomParticipant.objects.filter(room=room)

    context = {
        'room': room,
        'quiz': room.quiz,
        'join_code': join_code,
        'participants': participants,  
    }

    return render(request, 'lobby.html', context)