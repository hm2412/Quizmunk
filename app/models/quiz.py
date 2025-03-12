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

    name = models.CharField(blank=True, max_length=50)
    subject = models.CharField(blank=True, max_length=50)
    difficulty = models.CharField(blank=True, max_length=1, choices=DIFFICULTIES)
    type = models.CharField(max_length=1, choices=TYPES, blank=True)
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
    question_text = models.CharField(max_length=255)
    position = models.IntegerField(blank=True, null=True)
    time = models.PositiveIntegerField()
    quiz = models.ForeignKey(
        Quiz,
        related_name="questions",  # Positional argument
        on_delete=models.CASCADE,
        verbose_name="Related quiz",  # Keyword argument
        help_text="The quiz this question belongs to."
    )
    mark = models.IntegerField()
    image = models.ImageField(null=True, blank=True, upload_to='questions_images/')

    def __str__(self):
        return f"Quiz {self.quiz.id} Question {self.position}"

    class Meta:
        abstract = True
        ordering = ['position']

class IntegerInputQuestion(Question):
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
    is_correct = models.BooleanField()

    quiz = models.ForeignKey(
        Quiz,
        related_name="true_false_questions",  # Unique related_name, as above
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"TrueFalseQuestion: {self.question_text}, Correct: {self.is_correct}"
    
class TextInputQuestion(Question): # Can also be used for a fill in the blanks question.
    correct_answer = models.TextField()

    quiz = models.ForeignKey(
        Quiz,
        related_name="text_questions", 
        on_delete=models.CASCADE,
    )
    
    def __str__(self):
        return f"TextInputQuestion: {self.question_text}, Answer: {self.correct_answer}"

class DecimalInputQuestion(Question):
    correct_answer = models.DecimalField(max_digits=10, decimal_places=2)
    
    quiz = models.ForeignKey(
        Quiz,
        related_name="decimal_questions", 
        on_delete=models.CASCADE,
    )
    
    def __str__(self):
        return f"DecimalInputQuestion: {self.question_text}, Answer: {self.correct_answer}"

class MultipleChoiceQuestion(Question):
    options = models.JSONField() # Supports more than 4 choices
    correct_option = models.CharField(max_length=255)
    
    quiz = models.ForeignKey(
        Quiz,
        related_name="multiple_choice_questions", 
        on_delete=models.CASCADE,
    )
    
    def __str__(self):
        return f"MultipleChoiceQuestion: {self.question_text}, Correct: {self.correct_option}"
    
class NumericalRangeQuestion(Question):
    #this can be changed
    min_value = models.DecimalField(max_digits=10, decimal_places=10)
    max_value = models.DecimalField(max_digits=10, decimal_places=10)

    quiz = models.ForeignKey(
        Quiz,
        related_name="numerical_range_questions", 
        on_delete=models.CASCADE,
    )
    
    def __str__(self):
        return f"NumericalRangeQuestion: {self.question_text}, Accepted Range: {self.min_value}-{self.max_value}"

class SortingQuestion(Question):

    items = models.TextField()
   
    correct_order = models.CharField(max_length=200)

    quiz = models.ForeignKey(
        Quiz,
        related_name="sorting_questions",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"SortingQuestion: {self.question_text}"

    def get_items(self):
        
        return self.items.split(',')

    def get_correct_order(self):
        
        return [int(x) for x in self.correct_order.split(',')]

