from django.db import models
import string
import random

def generate_join_code():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=6))
        if not Room.objects.filter(join_code=code).exists():
            return code

class Room(models.Model):
    name = models.TextField(blank=False, max_length=50, help_text="Rooms must have a name")
    # tutor = models.ForeignKey(Tutor, related_name="room owners", on_delete=models.CASCADE)
    # quiz = models.ForeignKey(Quiz, related_name="Quiz chosen", on_delete=models.CASCADE)
    join_code = models.CharField(max_length=6, unique=True, editable=False, default=generate_join_code())
