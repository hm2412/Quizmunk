from django.db import models
from django.core.validators import RegexValidator
import uuid

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
