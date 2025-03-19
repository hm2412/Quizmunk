from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models.classroom import Classroom, ClassroomStudent, ClassroomInvitation

User = get_user_model()

class ViewTests(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            first_name="Stu",
            last_name="Dent",
            email_address="student@example.com",
            password="password123",
            role=User.STUDENT,
        )
        self.student_two = User.objects.create_user(
            first_name="Test",
            last_name="Student",
            email_address="student2@example.com",
            password="password123",
            role=User.STUDENT,
        )
        self.tutor_user = User.objects.create_user(
            first_name="Tu",
            last_name="Tor",
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
        self.classroom_student = ClassroomStudent.objects.create(classroom=self.classroom_one, student=self.student_user)

    def test_unauthenticated_user_redirects(self):
        response = self.client.get(reverse("student_classroom_view"))
        self.assertRedirects(response, reverse("homepage"))

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

    def test_tutor_can_create_classroom(self):
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(reverse("tutor_classroom_view"), {
            'classroom_name': 'New Class',
            'description': 'Test Description'
        })
        self.assertEqual(Classroom.objects.count(), 3)
        self.assertRedirects(response, '/tutor-classrooms/#')

    def test_tutor_can_delete_own_classroom(self):
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(
            reverse("tutor_classroom_detail", args=[self.classroom_one.id]),
            {'action': 'delete_classroom'}
        )
        self.assertEqual(Classroom.objects.count(), 1)
        self.assertRedirects(response, reverse("tutor_classroom_view"))

    def test_tutor_cannot_delete_others_classroom(self):
        self.client.login(email_address="tutor_2@email.com", password="password123")
        response = self.client.post(
            reverse("tutor_classroom_detail", args=[self.classroom_one.id]),
            {'action': 'delete_classroom'}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Classroom.objects.count(), 2)

    def test_tutor_can_invite_student(self):
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(
            reverse("tutor_classroom_detail", args=[self.classroom_one.id]),
            {
                'action': 'invite_student',
                'student_email': 'student2@example.com'
            }
        )
        self.assertTrue(ClassroomInvitation.objects.filter(
            student=self.student_two,
            classroom=self.classroom_one
        ).exists())
        self.assertRedirects(response, f'/tutor-classrooms/{self.classroom_one.id}/#')

    def test_cannot_invite_already_invited_student(self):
        ClassroomInvitation.objects.create(
            student=self.student_two,
            classroom=self.classroom_one
        )
        
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(
            reverse("tutor_classroom_detail", args=[self.classroom_one.id]),
            {
                'action': 'invite_student',
                'student_email': 'student2@example.com'
            }
        )
        self.assertEqual(
            ClassroomInvitation.objects.filter(
                student=self.student_two,
                classroom=self.classroom_one
            ).count(),
            1
        )
        self.assertRedirects(response, f'/tutor-classrooms/{self.classroom_one.id}/#create-invite-modal')

    def test_cannot_invite_nonexistent_student(self):
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(
            reverse("tutor_classroom_detail", args=[self.classroom_one.id]),
            {
                'action': 'invite_student',
                'student_email': 'nonexistent@example.com'
            }
        )
        self.assertRedirects(response, f'/tutor-classrooms/{self.classroom_one.id}/#create-invite-modal')

    def test_cannot_invite_tutor(self):
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(
            reverse("tutor_classroom_detail", args=[self.classroom_one.id]),
            {
                'action': 'invite_student',
                'student_email': 'tutor_2@email.com'
            }
        )
        self.assertRedirects(response, f'/tutor-classrooms/{self.classroom_one.id}/#create-invite-modal')

    def test_tutor_can_remove_student(self):
        self.client.login(email_address="tutor@example.com", password="password123")
        response = self.client.post(
            reverse("tutor_classroom_detail", args=[self.classroom_one.id]),
            {
                'action': 'remove_student',
                'student_id': self.student_user.id
            }
        )
        self.assertFalse(
            ClassroomStudent.objects.filter(
                student=self.student_user,
                classroom=self.classroom_one
            ).exists()
        )
        self.assertRedirects(response, reverse("tutor_classroom_detail", args=[self.classroom_one.id]))

    def test_tutor_can_edit_description(self):
        self.client.login(email_address="tutor@example.com", password="password123")
        new_description = "Updated description"
        response = self.client.post(
            reverse("tutor_classroom_detail", args=[self.classroom_one.id]),
            {
                'action': 'edit_description',
                'description': new_description
            }
        )
        self.classroom_one.refresh_from_db()
        self.assertEqual(self.classroom_one.description, new_description)
        self.assertRedirects(response, reverse("tutor_classroom_detail", args=[self.classroom_one.id]))