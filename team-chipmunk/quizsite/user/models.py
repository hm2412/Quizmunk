from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import uuid

class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model."""
    
    STUDENT = 'student'
    TUTOR = 'tutor'

    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (TUTOR, 'Tutor'),
    ]

    email_address = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={'unique': _("A user with this email already exists.")},
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=STUDENT,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Required (unique identifier)
    USERNAME_FIELD = 'email_address'

    def __str__(self):
        return self.email_address

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