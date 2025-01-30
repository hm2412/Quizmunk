from django.shortcuts import render
from django.http import Http404
import qrcode
from quizsite.app.models import Room

def lobby(request, code):
    try:
        room = Room.objects.get(join_code = code)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=1,
        )
        qr.add_data(request.build_absolute_uri())
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save("quizsite/app/static/images/qr_code.png")
        context = {
            'code': f"Room Code: {room.join_code}",
            'name': f"{room.name}",
        }
    except:
        raise Http404(f"Could not find room with code: {code}")
    else:
        return render(request, 'lobby.html', context)