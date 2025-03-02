from django.db import models

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
        limit_choices_to={"role": "student"}
    )