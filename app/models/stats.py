from django.db import models
from django.db.models.aggregates import Avg

from app.models import Room, RoomParticipant
from app.models.quiz import Quiz

class Stats(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    date_played = models.DateTimeField(auto_now_add=True)
    num_participants = models.IntegerField()
    mean_score = models.DecimalField(max_digits=5, decimal_places=2)


    def calculate_median(self):
        scores = RoomParticipant.objects.filter(room=self.room).values_list('score', flat=True).order_by('score')
        total_scores = len(scores)
        if total_scores == 0:
            self.median_mark = 0
        elif total_scores % 2 == 1:
            self.median_mark = scores[total_scores // 2]
        else:
            mid1 = scores[(total_scores // 2) - 1]
            mid2 = scores[total_scores // 2]
            self.median_mark = (mid1 + mid2) / 2

    def save(self, *args, **kwargs):
        self.num_participants = RoomParticipant.objects.filter(room=self.room).count()
        self.mean_score = RoomParticipant.objects.filter(room=self.room).aggregate(Avg('score'))['mean_score']
        self.median_mark = self.calculate_median()

    def __str__(self):
        return f"Stats for Room {self.room} and Quiz {self.quiz} on {self.date_played.strftime('%Y-%m-%d %H:%M:%S')}"


