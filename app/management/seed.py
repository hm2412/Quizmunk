import django
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quizsite.settings")
django.setup()

from quizsite.app.models import Room, generate_join_code

rooms = ["room1","room2","room3","room4","room5"]

for room in rooms:
    join_code = generate_join_code()  
    myRoom, created = Room.objects.get_or_create(name=room, join_code=join_code)
    if created:
        print(f"✅ Created Room: {room} | Join Code: {join_code}")
    else:
        print(f"⚠️ Room {room} already exists!")