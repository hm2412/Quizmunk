import os
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
import qrcode
from quizsite.app.models import Room, RoomParticipant, GuestAccess

def lobby(request, join_code):
    room = get_object_or_404(Room, join_code=join_code)

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
    qr_code_path = "quizsite/app/static/images/qr_code.png"

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

    
    context = {
        'room': room,
        'quiz': room.quiz,
        'join_code': join_code,
        'participants': participants,  
        'code': f"Room Code: {room.join_code}",
        'name': f"{room.name}",
        'qr_code_path': "/static/images/qr_code.png" if qr_code_path else None,
    }

    return render(request, 'lobby.html', context)