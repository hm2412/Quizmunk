from django.shortcuts import render
from django.http import Http404
from quizsite.app.models import Room

def lobby(request, code):
    try:
        room = Room.objects.get(join_code = code)
        context = {
            'code': f"Room Code: {room.join_code}",
            'name': f"{room.name}",
        }
    except:
        raise Http404(f"Could not find room with code: {code}")
    else:
        return render(request, 'lobby.html', context)