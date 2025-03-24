from django.core.exceptions import ValidationError
from django.db import models

from app.models import TrueFalseQuestion, IntegerInputQuestion, Room
from app.models.quiz import TextInputQuestion, DecimalInputQuestion, MultipleChoiceQuestion, NumericalRangeQuestion, \
    SortingQuestion
from app.models.user import User
from app.models.guest import GuestAccess


class Response(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    guest_access = models.ForeignKey(GuestAccess, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    correct = models.BooleanField(null=True, blank=True)

    class Meta:
        abstract = True
        
class TrueFalseResponse(Response):
    question = models.ForeignKey(TrueFalseQuestion, on_delete=models.CASCADE)
    answer = models.BooleanField()

    def __str__(self):
        if self.player:
            actor = self.player.email_address
        else:
            actor = f"Guest ({self.guest_access.session_id[:8]})"
        return f"True/False Answer by {actor} for question {self.question}: {self.answer}"


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
        if self.player:
            actor = self.player.email_address
        else:
            actor = f"Guest ({self.guest_access.session_id[:8]})"
        return f"Integer Input Answer by {actor} for question {self.question}: {self.answer}"

class TextInputResponse(Response):
    question = models.ForeignKey(TextInputQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)

    def __str__(self):
        if self.player:
            actor = self.player.email_address
        else:
            actor = f"Guest ({self.guest_access.session_id[:8]})"
        return f"Text Input Answer by {actor} for question {self.question}"

class DecimalInputResponse(Response):
    question = models.ForeignKey(DecimalInputQuestion, on_delete=models.CASCADE)
    answer = models.DecimalField(max_digits=10, decimal_places=2)

class MultipleChoiceResponse(Response):
    question = models.ForeignKey(MultipleChoiceQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)

    def clean(self):
        answer_stripped = self.answer.strip() if isinstance(self.answer, str) else self.answer
        options_stripped = [option.strip() for option in self.question.options]
        if answer_stripped not in options_stripped:
            raise ValidationError("Answer must be one of the following options: '{}'".format(self.question.options))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class NumericalRangeResponse(Response):
    question = models.ForeignKey(NumericalRangeQuestion, on_delete=models.CASCADE)
    answer = models.FloatField()

    def __str__(self):
        if self.player:
            actor = self.player.email_address
        else:
            actor = f"Guest ({self.guest_access.session_id[:8]})"
        return f"Numerical Range Answer by {actor} for question {self.question}"

class SortingResponse(Response):
    question = models.ForeignKey(SortingQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)

    def __str__(self):
        if self.player:
            actor = self.player.email_address
        else:
            actor = f"Guest ({self.guest_access.session_id[:8]})"
        return f"Sorting Answer by {actor} for question {self.question}"