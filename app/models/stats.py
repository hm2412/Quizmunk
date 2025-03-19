from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.aggregates import Avg
from django.db.models.expressions import result

from app.models import Room, RoomParticipant, Response, Quiz, Question, IntegerInputResponse, TrueFalseResponse, \
    TextInputResponse, DecimalInputResponse, MultipleChoiceResponse, NumericalRangeResponse, SortingResponse, User


class Stats(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    date_played = models.DateTimeField(auto_now_add=True)
    num_participants = models.IntegerField()
    mean_score = models.DecimalField(max_digits=5, decimal_places=2)
    median_score = models.DecimalField(max_digits=5, decimal_places=2)


    def calculate_median(self):
        scores = RoomParticipant.objects.filter(room=self.room).values_list('score', flat=True).order_by('score')
        total_scores = len(scores)
        if total_scores == 0:
            median = 0
        elif total_scores % 2 == 1:
            median = scores[total_scores // 2]
        else:
            mid1 = scores[(total_scores // 2) - 1]
            mid2 = scores[total_scores // 2]
            median = (mid1 + mid2) / 2
        return median

    def save(self, *args, **kwargs):
        self.num_participants = RoomParticipant.objects.filter(room=self.room).count()
        self.mean_score = RoomParticipant.objects.filter(room=self.room).aggregate(Avg('score'))['score__avg']
        if self.mean_score is None:
            self.mean_score = 0
        self.median_score = self.calculate_median()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Stats for Room {self.room} and Quiz {self.quiz} on {self.date_played.strftime('%Y-%m-%d %H:%M:%S')}"


class QuestionStats(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    question_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    question_id = models.PositiveIntegerField()
    question = GenericForeignKey('question_type', 'question_id')
    responses_received = models.IntegerField()
    correct_responses = models.IntegerField()
    percentage_correct = models.DecimalField(max_digits=5, decimal_places=2)


    def save(self, *args, **kwargs):
        from app.helpers.helper_functions import get_response_model_class
        response_model = get_response_model_class(self.question_type)
        self.responses_received = response_model.objects.filter(room=self.room, question=self.question).count()
        print(self.responses_received)
        self.correct_responses = response_model.objects.filter(room=self.room, question=self.question, correct=True).count()
        if self.responses_received != 0:
            self.percentage_correct = (self.correct_responses / self.responses_received) * 100
        else:
            self.percentage_correct = 100

        super(QuestionStats, self).save(*args, **kwargs)
