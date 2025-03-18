from django.db import models
from app.models.user import User

class Classroom(models.Model):
    name = models.CharField(max_length=50)
    tutor = models.ForeignKey(
        'app.User',
        related_name="tutor_classrooms",
        on_delete=models.CASCADE,
        limit_choices_to={"role": "tutor"}
    )
    description = models.CharField(max_length=255)

class ClassroomStudent(models.Model):
    classroom = models.ForeignKey(Classroom, related_name="students", on_delete=models.CASCADE)
    student = models.ForeignKey(
        'app.User',
        related_name="student_classrooms",
        on_delete=models.CASCADE,
        limit_choices_to={"role": User.STUDENT}
    )

    class Meta:
        unique_together = ('classroom', 'student')

class ClassroomInvitation(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    student = models.ForeignKey(
        User,
        related_name="classroom_invitations",
        on_delete=models.CASCADE,
        limit_choices_to={"role": User.STUDENT}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('declined', 'Declined')
        ],
        default='pending'
    )

    class Meta:
        unique_together = ('classroom', 'student')