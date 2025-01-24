from django.db import models

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