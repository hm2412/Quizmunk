from django.db import models
from app.models.user import User

class Classroom(models.Model):
    name = models.CharField(max_length=50)
    tutor = models.ForeignKey(
        User,
        related_name="tutor_classrooms",
        on_delete=models.CASCADE,
        limit_choices_to={"role": User.TUTOR}
    )
    description = models.CharField(max_length=255)

class ClassroomStudent(models.Model):
    classroom = models.ForeignKey(Classroom, related_name="students", on_delete=models.CASCADE)
    student = models.ForeignKey(
        User,
        related_name="student_classrooms",
        on_delete=models.CASCADE,
        limit_choices_to={"role": User.STUDENT}
    )