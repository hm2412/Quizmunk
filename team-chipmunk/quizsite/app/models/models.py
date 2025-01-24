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

class Quiz(models.Model):
    DIFFICULTIES = {
        "E": "Easy",
        "M": "Medium",
        "H": "Hard",
    }
    TYPES = {
        "L": "Live",
        "R": "Releasable",
    }

    ID = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    tutorID = models.CharField(max_length=10)
    subject = models.CharField(blank=True, max_length=50)
    difficulty = models.CharField(blank=True, max_length=1, choices=DIFFICULTIES)
    type = models.CharField(max_length=1, choices=TYPES)

    def __str__(self):
        return(f"Quiz: {self.ID}, {self.name} - made by tutor {self.tutorID} and is {type}")

    class Meta:
        abstract = True

class Question(models.Model):
    number = models.IntegerField()
    time = models.IntegerField()
    quizID = models.CharField(max_length=10)

    def __str__(self):
        return (f"Quiz {self.quizID} Question {self.number}")

    class Meta:
        abstract = True

class IntegerInputQuestion(Question):
    question_text = models.CharField(max_length=255)
    mark = models.IntegerField()
    correct_answer = models.IntegerField()

    def __str__(self):
        return f"IntegerInputQuestion: {self.question_text}, Answer: {self.correct_answer}"

class TrueFalseQuestion(Question):
    question_text = models.CharField(max_length=255)
    is_correct = models.BooleanField() 
    mark = models.IntegerField()

    def __str__(self):
        return f"TrueFalseQuestion: {self.question_text}, Correct: {self.is_correct}"
