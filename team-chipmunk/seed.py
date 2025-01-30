from quizsite.app.models import Room

rooms = ["room1","room2","room3","room4","room5"]

for room in rooms:
    myRoom = Room.objects.create(name=room)