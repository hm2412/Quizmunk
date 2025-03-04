from django.core.exceptions import ValidationError
from django.db import models

from app.models import TrueFalseQuestion, IntegerInputQuestion, Room
from app.models.quiz import TextInputQuestion, DecimalInputQuestion, MultipleChoiceQuestion, NumericalRangeQuestion, \
    SortingQuestion
from app.models.user import User

class Response(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

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

class TextInputResponse(Response):
    question = models.ForeignKey(TextInputQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)

    def __str__(self):
        return f"Text Input Answer by {self.player} for question {self.question}"

class DecimalInputResponse(Response):
    question = models.ForeignKey(DecimalInputQuestion, on_delete=models.CASCADE)
    answer = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Decimal Input Answer by {self.player} for question {self.question}"

class MultipleChoiceResponse(Response):
    question = models.ForeignKey(MultipleChoiceQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)

    def __str__(self):
        return f"Multiple Choice Answer by {self.player} for question {self.question}"

class NumericalRangeResponse(Response):
    question = models.ForeignKey(NumericalRangeQuestion, on_delete=models.CASCADE)
    answer = models.IntegerField()

    def __str__(self):
        return f"Numerical Range Answer by {self.player} for question {self.question}"

class SortingResponse(Response):
    question = models.ForeignKey(SortingQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)

    def __str__(self):
        return f"Sorting Answer by {self.player} for question {self.question}"