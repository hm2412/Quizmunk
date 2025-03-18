from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models.classroom import Classroom, ClassroomStudent, ClassroomInvitation

User = get_user_model()

class ViewTests(TestCase):
    def setUp(self):
        # Create a student user
        self.student_user = User.objects.create_user(
            first_name="Stu",
            last_name="Dent",
            email_address="student@example.com",
            password="password123",
            role=User.STUDENT,
        )
        # Create a tutor user
        self.tutor_user = User.objects.create_user(
            first_name="Tu",
            last_name = "Tor",
            email_address="tutor@example.com",
            password="password123",
            role=User.TUTOR,
        )

        self.tutor_two = User.objects.create_user(
            first_name="test",
            last_name="tutor",
            email_address="tutor_2@email.com",
            password="password123",
            role=User.TUTOR
        )

        self.classroom_one = Classroom.objects.create(name="Classroom_1", tutor=self.tutor_user,description="test class one")
        self.classroom_two = Classroom.objects.create(name="Classroom_2", tutor=self.tutor_user,description="test class two")

        #student is in class one but not in class two
        classroom_student = ClassroomStudent.objects.create(classroom=self.classroom_one, student=self.student_user)


    def test_unauthenticated_user_redirects(self):
        # Unauthenticated user tries to access student classrooms
        response = self.client.get(reverse("student_classroom_view"))
        self.assertRedirects(response, reverse("homepage"))

        # Unauthenticated user tries to access tutor classrooms
        response = self.client.get(reverse("tutor_classroom_view"))
        self.assertRedirects(response, reverse("homepage"))

    def test_student_can_access_student_classrooms(self):
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("student_classroom_view"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student/classrooms.html")
    
    def test_student_cannot_access_tutor_classrooms(self):
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("tutor_classroom_view"))
        self.assertEqual(response.status_code, 403)

    def test_tutor_can_access_tutor_classrooms(self):
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("tutor_classroom_view"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tutor/classroom_view.html")

    
    def test_tutor_cannot_access_student_classrooms(self):
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("student_classroom_view"))
        self.assertEqual(response.status_code, 403)

    def test_student_can_access_right_class(self):
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("student_classroom_detail_view", args=[self.classroom_one.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student/classroom_detail.html")

    def test_student_cannot_access_wrong_class(self):
        #test student is not in classroom two
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("student_classroom_detail_view", args=[self.classroom_two.id]))
        self.assertEqual(response.status_code, 404)
    
    def test_tutor_cannot_access_class_as_student(self):
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.get(reverse("student_classroom_detail_view", args=[self.classroom_one.id]))
        self.assertEqual(response.status_code, 403)

    def test_student_cannot_access_class_as_tutor(self):
        self.client.login(email_address="student@example.com", password="password123")
        response = self.client.get(reverse("tutor_classroom_detail", args=[self.classroom_one.id]))
        self.assertEqual(response.status_code, 403)

