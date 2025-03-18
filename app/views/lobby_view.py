import os
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
import qrcode
from app.models import Room, RoomParticipant, Quiz, GuestAccess
from app.models.classroom import Classroom, ClassroomStudent
from app.helpers.decorators import is_tutor
from app.views.live_quiz_view import tutor_live_quiz

@is_tutor
def setup_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    room = Room.objects.create(name=f"{quiz.name} Room", quiz=quiz, quiz_started=False)

    return redirect(lobby, join_code=room.join_code)

def lobby(request, join_code):
    room = get_object_or_404(Room, join_code=join_code)

    n_classroom = False
     
    if room.classroom is not None:
         if request.user.is_authenticated:
             if ClassroomStudent.objects.filter(classroom_id=room.classroom.id, student=request.user).exists():
                 participant, created = RoomParticipant.objects.get_or_create(room=room, user=request.user)
                 in_classroom = True
             elif request.user.role == 'tutor':
                 in_classroom = True
    else:
        if request.user.is_authenticated:
             participant, created = RoomParticipant.objects.get_or_create(room=room, user=request.user)
        else:
            guest_session = request.session.session_key
        if not guest_session:
            request.session.save()
            guest_session = request.session.session_key
        guest_access, _ = GuestAccess.objects.get_or_create(session_id=guest_session)
        participant, created = RoomParticipant.objects.get_or_create(room=room, guest_access=guest_access)

    participants = RoomParticipant.objects.filter(room=room).exclude(user__role="tutor")
    qr_code_path = "app/static/images/qr_code.png"

    try:
        os.makedirs(os.path.dirname(qr_code_path), exist_ok=True)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=1,
        )
        qr.add_data(request.build_absolute_uri())
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(qr_code_path)
        
    except Exception as e:
        messages.error(request, f"QR Code generation failed: {e}") 
        qr_code_path = None  

    #if not room.quiz:
    #    messages.error(request, 'Invalid code!')
    #    return redirect('join_quiz')
    if request.method == 'POST':
        # Redirect to start quiz functionality
        return redirect(tutor_live_quiz, join_code=room.join_code, )
    
    context = {
        'room': room,
        'quiz': room.quiz,
        'join_code': join_code,
        'participants': participants,  
        'code': f"Room Code: {room.join_code}",
        'name': f"{room.name}",
        'qr_code_path': "/static/images/qr_code.png" if qr_code_path else None,
        'in_classroom': in_classroom,
    }

    return render(request, 'lobby.html', context)

@is_tutor
def setup_classroom_quiz(request, quiz_id, classroom_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    classroom = Classroom.objects.get(id=classroom_id)
    room = Room.objects.create(name=f"{quiz.name} Room", quiz=quiz, classroom=classroom)
    return redirect(lobby, join_code=room.join_code)