from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import uuid
import string
import random


class UserManager(BaseUserManager):
    # creates and saves regular user in db
    def create_user(self, email_address, password=None, **extra_fields):
        if not email_address:
            raise ValueError('The Email Address field must be set')
        email_address = self.normalize_email(email_address)
        user = self.model(email_address=email_address, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # creates and saves a superuser(admin) in the db
    def create_superuser(self, email_address, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email_address, password, **extra_fields)

    # retrieves user by email address
    # this function seems unnecessary?
    def get_by_natural_key(self, email_address):
        return self.get(email_address=email_address)


class User(AbstractBaseUser, PermissionsMixin):
    STUDENT = 'student'
    TUTOR = 'tutor'

    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (TUTOR, 'Tutor'),
    ]

    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email_address = models.EmailField(unique=True)
    role = models.CharField(
        max_length=7,
        choices=ROLE_CHOICES,
        default=STUDENT,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    # Required (unique identifier)
    USERNAME_FIELD = 'email_address'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email_address

    class Meta:
        ordering = ['email_address']


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
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        if not Room.objects.filter(join_code=code).exists():
            return code



class Room(models.Model):
    name = models.CharField(blank=False, max_length=50, help_text="Rooms must have a name")
    quiz = models.ForeignKey(
        Quiz, 
        related_name="room_set", 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="Current quiz",
        help_text="The quiz this room is made from."
    )
    join_code = models.CharField(max_length=8, unique=True, editable=False, default=generate_join_code)

    def __str__(self):
        return f"Room: {self.name} (Code: {self.join_code})"


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
        return (f"Quiz: {self.ID}, {self.name} - made by tutor {self.tutorID} and is {type}")

class Question(models.Model):
    MARKS=[
        ("5": "5 marks"),
        ("10": "10 marks"),
        ("15": "15 marks"),
        ("2O": "20 marks"),
        ("25": "25 marks"),
        ("30": "30 marks"),
    ]
    TIMES={
        ("5": "5 seconds"),
        ("10": "10 seconds"),
        ("15": "15 seconds"),
        ("2O": "20 seconds"),
        ("25": "25 seconds"),
        ("30": "30 seconds"),
    }
    number = models.IntegerField(blank=True, null=True)
    time = models.CharField(blank=True, max_length=2, choices=TIMES)
    quiz = models.ForeignKey(
        Quiz, 
        on_delete=models.CASCADE, 
        related_name"questions",
        verbose_name="Related quiz", 
        help_text="The quiz this question belongs to."
    )
    mark = models.CharField(blank=True, max_length=2, choices=MARKS)

    def __str__(self):
        return (f"Quiz {self.quizID} Question {self.number}")

    class Meta:
        abstract = True

class IntegerInputQuestion(Question):
    question_text = models.CharField(max_length=255)
    correct_answer = models.IntegerField()

    def __str__(self):
        return f"IntegerInputQuestion: {self.question_text}, Answer: {self.correct_answer}"

class TrueFalseQuestion(Question):
    question_text = models.CharField(max_length=255)
    is_correct = models.BooleanField()

    def __str__(self):
        return f"TrueFalseQuestion: {self.question_text}, Correct: {self.is_correct}"

class RoomParticipant(models.Model):
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE, 
        related_name='participants',
        verbose_name="Room",
        help_text="The room this participant belongs to."
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="User",
        help_text="A registered user participating in the room."
    )
    guest_access = models.ForeignKey(
        GuestAccess,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Guest Access",
        help_text="Guest access session for the participant."
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(user__isnull=False, guest_access__isnull=True) |
                    models.Q(user__isnull=True, guest_access__isnull=False)
                ),
                name='user_xor_guest'
            )
        ]

    def clean(self):
        if self.user and self.guest_access:
            raise ValidationError("Only one of 'user' OR 'guest_access' can be set.")
        if not self.user and not self.guest_access:
            raise ValidationError("Either user or guest_access must be set.")

    def __str__(self):
        if self.user:
            return f"User: {self.user.email_address}"
        return f"Guest: {self.guest_access.session_id[:8]}"

class Classroom(models.Model):
    name = models.CharField(max_length=50)
    tutor = models.ForeignKey(
        User,
        related_name="classrooms",
        on_delete=models.CASCADE,
        limit_choices_to={"role": User.TUTOR}
    )
    description = models.CharField(max_length=255)

class ClassroomStudent(models.Model):
    classroom = models.ForeignKey(Classroom, related_name="students", on_delete=models.CASCADE)
    student = models.ForeignKey(
        User,
        related_name="classrooms",
        on_delete=models.CASCADE,
        limit_choices_to={"role": User.STUDENT}
    )

