from django.db import models
from app.models.user import User
from django.core.files.storage import default_storage
from django.core.exceptions import ObjectDoesNotExist
from itertools import chain


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
    is_public = models.BooleanField(default=False, help_text="If true, quiz will be visible to all tutors")
    tutor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'Tutor'},  # Ensures only tutors can own quizzes
        related_name='quizzes',
        verbose_name="Related tutor",
        help_text="The tutor that creates this quiz."
    )
    quiz_img = models.ImageField(
        upload_to='quiz_thumbnail/',
        null=True,
        blank=True
    )

    # room = models.OneToOneField("Room", related_name="quiz_room", on_delete=models.SET_NULL, null=True, blank=True)
    # I believe this should be removed, as it's redundant? 

    def get_all_questions(self):
        # This method already uses specific question types
        integer_qs = self.integer_questions.all()
        true_false_qs = self.true_false_questions.all()
        text_qs = self.text_questions.all()
        decimal_qs = self.decimal_questions.all()
        multiple_choice_qs = self.multiple_choice_questions.all()
        numerical_range_qs = self.numerical_range_questions.all()
        sorting_qs = self.sorting_questions.all()

        # Combine all queries
        all_questions = list(chain(integer_qs, true_false_qs, text_qs, decimal_qs, multiple_choice_qs, numerical_range_qs, sorting_qs))

        # Sort by position
        return sorted(all_questions, key=lambda q: q.position if q.position is not None else float('inf'))


    def __str__(self):
        return (f"Quiz: {self.id}, {self.name} - made by tutor {self.tutor}")

class Question(models.Model):
    question_text = models.CharField(max_length=255)
    position = models.IntegerField(blank=True, null=True)
    time = models.PositiveIntegerField(default=30)
    quiz = models.ForeignKey(
        Quiz,
        related_name="questions",  # Positional argument
        on_delete=models.CASCADE,
        verbose_name="Related quiz",  # Keyword argument
        help_text="The quiz this question belongs to."
    )
    mark = models.PositiveIntegerField()
    image = models.ImageField(null=True, blank=True, upload_to='questions_images/')

    def save(self, *args, **kwargs):
        """ Delete the associated image file when the image is updated """
        if self.pk:
            try:
                old_instance = self.__class__.objects.get(pk=self.pk)
                if old_instance.image and self.image != old_instance.image:
                    if default_storage.exists(old_instance.image.name):
                        default_storage.delete(old_instance.image.name)
            except ObjectDoesNotExist:
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """ Delete the associated image file when the question is deleted. """
        if self.image:
            if default_storage.exists(self.image.name):
                default_storage.delete(self.image.name)
        super().delete(*args, **kwargs)

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
    correct_answer = models.BooleanField()

    quiz = models.ForeignKey(
        Quiz,
        related_name="true_false_questions",  # Unique related_name, as above
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"TrueFalseQuestion: {self.question_text}, Correct: {self.correct_answer}"
    
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
    correct_answer = models.CharField(max_length=255)
    
    quiz = models.ForeignKey(
        Quiz,
        related_name="multiple_choice_questions", 
        on_delete=models.CASCADE,
    )
    
    def __str__(self):
        return f"MultipleChoiceQuestion: {self.question_text}, Correct: {self.correct_answer}"
    
class NumericalRangeQuestion(Question):
    #this can be changed
    min_value = models.FloatField()
    max_value = models.FloatField()

    quiz = models.ForeignKey(
        Quiz,
        related_name="numerical_range_questions", 
        on_delete=models.CASCADE,
    )
    
    def __str__(self):
        return f"NumericalRangeQuestion: {self.question_text}, Accepted Range: {self.min_value}-{self.max_value}"
    
    @property
    def correct_answer(self):
        # Return the accepted range as a string.
        return f"{self.min_value} - {self.max_value}"

class SortingQuestion(Question):

    options = models.JSONField()

    quiz = models.ForeignKey(
        Quiz,
        related_name="sorting_questions",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"SortingQuestion: {self.question_text}"

    def get_items(self):
        
        return self.options

