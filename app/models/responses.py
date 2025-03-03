from django.db import models

from app.models import TrueFalseQuestion, IntegerInputQuestion
from app.models.user import User

class Response(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class TrueFalseResponse(Response):
    question = models.ForeignKey(TrueFalseQuestion, on_delete=models.CASCADE)
    answer = models.BooleanField()

    def __str__(self):
        return f"True/False Answer by {self.player} for question {self.question}: {self.answer}"


class IntegerInputResponse(Response):
    question = models.ForeignKey(IntegerInputQuestion, on_delete=models.CASCADE)
    answer = models.IntegerField()

    def __str__(self):
        return f"Integer Input Answer by {self.player} for question {self.question}: {self.answer}"