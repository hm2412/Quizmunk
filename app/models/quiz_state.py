from django.db import models
from app.models.room import Room

class QuizState(models.Model):
    room = models.OneToOneField(Room, on_delete=models.CASCADE)
    current_question_index = models.IntegerField(default=0)
    quiz_started = models.BooleanField(default=False)

    def next_question(self):
        self.current_question_index += 1
        self.save()