from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import uuid
import string
import random

class UserManager(BaseUserManager):
    #creates and saves regular user in db
    def create_user(self, email_address, username, password=None, **extra_fields):
        if not email_address:
            raise ValueError('The Email Address field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        
        email_address = self.normalize_email(email_address)
        user = self.model(email_address=email_address, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    #creates and saves a superuser(admin) in the db
    def create_superuser(self, email_address, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email_address, username, password, **extra_fields)
    #retrieves user by email address
    def get_by_natural_key(self, email_address):
        return self.get(email_address=email_address)
    
class User(AbstractBaseUser, PermissionsMixin):
    STUDENT = 'student'
    TUTOR = 'tutor'

    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (TUTOR, 'Tutor'),
    ]

    email_address = models.EmailField(unique=True)
    username = models.CharField(max_length=50,unique=True)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=STUDENT,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects= UserManager()
    # Required (unique identifier)
    USERNAME_FIELD = 'email_address'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['email_address']


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"Student: {self.name}"


class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tutor_profile')
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"Tutor: {self.name}"

class GuestAccess(models.Model):
    """Model for guests without an account."""
    classroom_code = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9]*$',
                message='Classroom code must be alphanumeric.',
                code='invalid_classroom_code'
            )
        ]
    )
    session_id = models.CharField(max_length=100, unique=True)  # Unique session ID for tracking
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())  # Generate a unique session ID
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Guest - Classroom Code: {self.classroom_code}"

def generate_join_code():
    from django.apps import apps
    Room = apps.get_model('app', 'Room')  # Dynamically load the Room model
    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=6))
        if not Room.objects.filter(join_code=code).exists():
            return code

class Room(models.Model):
    name = models.TextField(blank=False, max_length=50, help_text="Rooms must have a name")
    # tutor = models.ForeignKey(Tutor, related_name="room owners", on_delete=models.CASCADE)
    # quiz = models.ForeignKey(Quiz, related_name="Quiz chosen", on_delete=models.CASCADE)
    join_code = models.CharField(max_length=6, unique=True, editable=False, default=generate_join_code)

    def __str__(self):
        return f"Room: {self.name} (Code: {self.join_code})"

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
