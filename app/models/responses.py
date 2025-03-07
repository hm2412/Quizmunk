from django.core.exceptions import ValidationError
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

    def clean(self):
        # Custom validation for the answer field
        if isinstance(self.answer, float):
            raise ValidationError("Answer must be an integer.")
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Integer Input Answer by {self.player} for question {self.question}: {self.answer}"