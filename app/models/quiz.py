from django.db import models
from app.models.user import User

class Quiz(models.Model):
    DIFFICULTIES = [
        ("E", "Easy"),
        ("M", "Medium"),
        ("H", "Hard"),
    ]
    TYPES = [
        ("L", "Live"),
        ("R", "Releasable"),
    ]

    name = models.CharField(max_length=50)
    subject = models.CharField(blank=True, max_length=50)
    difficulty = models.CharField(blank=True, max_length=1, choices=DIFFICULTIES)
    type = models.CharField(max_length=1, choices=TYPES)
    tutor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'Tutor'},  # Ensures only tutors can own quizzes
        related_name='quizzes',
        verbose_name="Related tutor",
        help_text="The tutor that creates this quiz."
    )
    # room = models.OneToOneField("Room", related_name="quiz_room", on_delete=models.SET_NULL, null=True, blank=True)
    # I believe this should be removed, as it's redundant? 


    def __str__(self):
        return (f"Quiz: {self.id}, {self.name} - made by tutor {self.tutor}")

class Question(models.Model):
    MARKS = [
        ("5", "5"),
        ("10", "10"),
        ("15", "15"),
        ("20", "20"),
        ("25", "25"),
        ("30", "30"),
    ]
    TIMES = [
        ("5", "5"),
        ("10", "10"),
        ("15", "15"),
        ("20", "20"),
        ("25", "25"),
        ("30", "30"),
    ]
    number = models.IntegerField(blank=True, null=True)
    time = models.CharField(blank=True, max_length=2, choices=TIMES)
    quiz = models.ForeignKey(
        Quiz,
        related_name="questions",  # Positional argument
        on_delete=models.CASCADE,
        verbose_name="Related quiz",  # Keyword argument
        help_text="The quiz this question belongs to."
    )
    mark = models.CharField(blank=True, max_length=2, choices=MARKS)

    def __str__(self):
        return f"Quiz {self.quiz.id} Question {self.number}"

    class Meta:
        abstract = True

class IntegerInputQuestion(Question):
    question_text = models.CharField(max_length=255)
    correct_answer = models.IntegerField()

    # This attribute is inherited but needs a unique related_name, which is why it's being overwritten here
    quiz = models.ForeignKey(
        Quiz,
        related_name="integer_questions", 
        on_delete=models.CASCADE,
    )


    def __str__(self):
        return f"IntegerInputQuestion: {self.question_text}, Answer: {self.correct_answer}"

class TrueFalseQuestion(Question):
    question_text = models.CharField(max_length=255)
    is_correct = models.BooleanField()

    quiz = models.ForeignKey(
        Quiz,
        related_name="true_false_questions",  # Unique related_name, as above
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"TrueFalseQuestion: {self.question_text}, Correct: {self.is_correct}"