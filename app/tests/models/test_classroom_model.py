from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from app.models.user import User
from app.models.classroom import Classroom, ClassroomStudent

class ClassroomTestCase(TestCase):
    def setUp(self):
        self.test_tutor = User.objects.create_user(email_address='tutor@example.com', first_name='Test', last_name='Tutor', role=User.TUTOR)
        self.test_student = User.objects.create_user(email_address='student@example.com', first_name='Test', last_name='Student', role=User.STUDENT)
        self.classroom = Classroom.objects.create(name="Test Classroom", tutor=self.test_tutor, description="A test classroom description")

    def test_valid_classroom_is_valid(self):
        try:
            self.classroom.full_clean()
        except ValidationError:
            self.fail("Default test classroom should be deemed valid")

    def test_classroom_name_max_length(self):
        with self.assertRaises(ValidationError):
            invalid_classroom = Classroom(
                name='A' * 51,  
                tutor=self.test_tutor,
                description="Invalid classroom"
            )
            invalid_classroom.full_clean()

    def test_classroom_description_max_length(self):
        with self.assertRaises(ValidationError):
            invalid_classroom = Classroom(
                name="Test Classroom",
                tutor=self.test_tutor,
                description='A' * 256  
            )
            invalid_classroom.full_clean()

    def test_classroom_student_creation(self):
        classroom_student = ClassroomStudent.objects.create(
            classroom=self.classroom,
            student=self.test_student
        )
        
        self.assertIsNotNone(classroom_student.id)
        self.assertEqual(classroom_student.classroom, self.classroom)
        self.assertEqual(classroom_student.student, self.test_student)
    
    def test_tutor_role_constraint(self):
        non_tutor_user = User.objects.create_user(
            email_address='non_tutor@example.com', 
            first_name='Non', 
            last_name='Tutor', 
            role=User.STUDENT
        )

        with self.assertRaises(ValidationError):
            invalid_classroom = Classroom(
                name="Invalid Classroom",
                tutor=non_tutor_user,
                description="Should not work"
            )
            invalid_classroom.full_clean()
    
    def test_multiple_students_in_classroom(self):
        additional_student1 = User.objects.create_user(
            email_address='student1@example.com', 
            first_name='Student', 
            last_name='One', 
            role=User.STUDENT
        )

        additional_student2 = User.objects.create_user(
            email_address='student2@example.com', 
            first_name='Student', 
            last_name='Two', 
            role=User.STUDENT
        )

        ClassroomStudent.objects.create(classroom=self.classroom, student=additional_student1)
        ClassroomStudent.objects.create(classroom=self.classroom, student=additional_student2)
        
        self.assertEqual(self.classroom.students.count(), 2)
