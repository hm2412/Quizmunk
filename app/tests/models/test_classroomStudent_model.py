from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from app.models.classroom import Classroom, ClassroomStudent
from app.models.user import User

class ClassroomStudentTestCase(TestCase):
    def setUp(self):
        self.tutor = User.objects.create_user(email_address="tutor@example.com", first_name="Tutor", last_name="User", role=User.TUTOR)
        self.student = User.objects.create_user(email_address='student@example.com', first_name='Student', last_name='User', role=User.STUDENT)
        self.classroom = Classroom.objects.create(name="Testing Class", tutor=self.tutor)
        self.classroom_student = ClassroomStudent.objects.create(classroom=self.classroom, student=self.student)
    def test_valid_classroom_student_is_valid(self):
        try:
            self.classroom_student.full_clean()
        except ValidationError:
            self.fail("Valid ClassroomStudent should be valid")

    def test_duplicate_classroom_student_is_invalid(self):
        with self.assertRaises(IntegrityError):
            ClassroomStudent.objects.create(classroom=self.classroom, student=self.student)

    def test_classroomless_student_is_invalid(self):
        with self.assertRaises(IntegrityError):
            ClassroomStudent.objects.create(classroom=None, student=self.student)
    def test_studentless_classroom_is_invalid(self):
        with self.assertRaises(IntegrityError):
            ClassroomStudent.objects.create(classroom=self.classroom, student=None)
