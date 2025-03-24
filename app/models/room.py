from django.db import models
from django.forms import ValidationError
from app.models import Classroom
from app.models.user import User
from app.models.guest import GuestAccess
from app.models.quiz import Quiz
from app.models.classroom import Classroom
import random
import string


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
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True)
    quiz_started = models.BooleanField(default=False)
    current_question_index = models.PositiveIntegerField(default=0)
    is_quiz_active = models.BooleanField(default=False)

    def get_questions(self):
        """Combine all question types safely"""
        if not self.quiz:
            return []

        questions = []
        question_types = [
            'integer_questions',
            'true_false_questions',
            'text_questions',
            'multiple_choice_questions',
            'decimal_questions',
            'numerical_range_questions',
            'sorting_questions'
        ]

        for q_type in question_types:
            questions += list(getattr(self.quiz, q_type).all())

        return sorted(questions, key=lambda q: q.position if q.position else 0)

    def get_current_question(self):
        questions = self.get_questions()
        if 0 <= self.current_question_index < len(questions):
            return questions[self.current_question_index]
        return None

    def next_question(self):
        self.current_question_index += 1
        self.save()
        return self.get_current_question()

    classroom = models.ForeignKey(
         Classroom,
         related_name="locked_rooms",
         on_delete=models.CASCADE,
         null=True,
         blank=True,
         help_text="The Classroom associated with this room"
    )    
    quiz_started = models.BooleanField(default=False)
    current_question_index = models.PositiveIntegerField(default=0)
    is_quiz_active = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Room: {self.name} (Code: {self.join_code})"

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
    score = models.IntegerField(default=0)

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

