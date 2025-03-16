from django.core.management.base import BaseCommand
from faker import Faker
from random import randint, shuffle
from app.models import ( 
    Classroom,
    ClassroomStudent,
    GuestAccess,
    Quiz,
    TrueFalseQuestion,
    IntegerInputQuestion,
    Room,
    RoomParticipant,
    User,
)

"""The way this seeder works is it adds TWO admins, TWO tutors, TWO known students and 94 random students.
It creates 4 small quizzes with random questions of both types and assigns then to ALICE tutor and it 
creates a classroom for BOB tutor where only John is a part of it, along with other random students."""

admin_fixtures = [
    {'email': 'Primary.Admin@example.org', 'first_name': 'Primary', 'last_name': 'Admin'},
    {'email': 'Secondary.Admin@example.org', 'first_name': 'Secondary', 'last_name': 'Admin'}
]

tutor_fixtures = [
    {'email': 'Alice.Tutor@example.org', 'first_name': 'Alice', 'last_name': 'Tutor'},
    {'email': 'Bob.Tutor@example.org', 'first_name': 'Bob', 'last_name': 'Tutor'}
]

user_fixtures = [
    {'email': 'John.Doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'email': 'Jane.Doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'}
]

class Command(BaseCommand):
    PASSWORD = "password123"
    USER_COUNT = 100
    ROOM_COUNT = 4
    CLASSROOM_SIZE = 10

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **kwargs):
        self.create_admin_fixtures()
        self.create_tutor_fixtures()
        self.create_user_fixtures()
        self.generate_users()
        self.generate_rooms()
        self.generate_classroom()

    "User generation functions"

    def create_user_fixtures(self):
        for data in user_fixtures:
            try:
                if not User.objects.filter(email_address = data['email']).exists():
                    User.objects.create_user(data['email'], data['first_name'], data['last_name'], Command.PASSWORD)
            except Exception as e:
                print(f"Error creating user {data['email']}: {e}")
        print("User fixtures seeded")

    def create_tutor_fixtures(self):
        for data in tutor_fixtures:
            try:
                if not User.objects.filter(email_address = data['email']).exists():
                    tutor = User.objects.create_user(data['email'], data['first_name'], data['last_name'], Command.PASSWORD)
                    tutor.role = User.TUTOR
                    tutor.save()
            except Exception as e:
                print(f"Error creating tutor {data['email']}: {e}")
        print("Tutor fixtures seeded")

    def create_admin_fixtures(self):
        for data in user_fixtures:
            try:
                if not User.objects.filter(email_address = data['email']).exists():
                    User.objects.create_superuser(data['email'], data['first_name'], data['last_name'], Command.PASSWORD)
            except Exception as e:
                print(f"Error creating admin {data['email']}: {e}")
        print("Admin fixtures seeded")
    
    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = first_name + '.' + last_name + "@example.org"
        try:
            if not User.objects.filter(email_address = email).exists():
                User.objects.create_user(email, first_name, last_name, Command.PASSWORD)
        except Exception as e:
            print(f"Error creating user {email}: {e}")

    def generate_users(self):
        user_count = User.objects.count()
        while user_count < Command.USER_COUNT:
            print(f"Seeding user {user_count}", end = "\r")
            try:
                self.generate_user()
            except:
                continue
            user_count += User.objects.count()
        print("Random users seeded")

    "Room generating functions"

    def generate_rooms(self):
        room_count = Room.objects.count()
        while room_count < Command.ROOM_COUNT:
            print(f"Seeding room {room_count + 1} / {Command.ROOM_COUNT}", end = "\r")
            try:
                self.generate_room()
            except:
                continue
            room_count = Room.objects.count()

    def generate_room(self):
        room_name = f"Room {Room.objects.count() + 1}"
        try:
            room = Room.objects.create(name = room_name)
            print(f"Created {room.name} (Code: {room.join_code})")
            self.create_quiz(room)
        except Exception as e:
            print(f"Error creating room {room_name}: {e}")

    def create_quiz(self, room):
        sample_quiz = Quiz.objects.create(
            name = f"Sample Quiz for {room.name}",
            subject = "Testing the questions",
            difficulty = "E",
            type = "L",
            tutor = User.objects.filter(email_address = "Alice.Tutor@example.org").first()
        )
        room.quiz = sample_quiz
        room.save()

        integer_answer = randint(1, 10)

        IntegerInputQuestion.objects.create(
            quiz = sample_quiz,
            question_text = f"The answer to this sample question is {integer_answer}",
            correct_answer = integer_answer
            
        )

        TrueFalseQuestion.objects.create(
            quiz = sample_quiz,
            question_text = f"The answer to this sample question is {str(integer_answer % 2 == 0)}",
            correct_answer = (integer_answer % 2 == 0)
        )

    "Classroom generating functions"

    def generate_classroom(self):
        bob = User.objects.filter(email_address = "Bob.Tutor@example.org").first()
        john = User.objects.filter(email_address = "John.Doe@example.org").first()

        classroom = Classroom.objects.create(
            name = "Bob's Classroom",
            tutor = bob,
            description = "Hi, I'm Bob. I don't know any of you except John and Jane!"
        )
        print(f"Created {classroom.name}", end = '\r')

        ClassroomStudent.objects.create(classroom = classroom, student = john)

        classroom_count = ClassroomStudent.objects.filter(classroom = Classroom.objects.filter(name = "Bob's Classroom").first()).count()
        students = list(User.objects.exclude(role = User.TUTOR, is_staff = True))

        while classroom_count < Command.CLASSROOM_SIZE:
            student = students.pop()
            ClassroomStudent.objects.create(classroom = classroom, student = student)
            print(f"Added {student.email_address} to {classroom.name}", end = "\r")
            classroom_count = ClassroomStudent.objects.filter(classroom = Classroom.objects.filter(name = "Bob's Classroom").first()).count()

        #There's a bug here where it will type "Classroom seeding complete.org to Bob's Classroomsroom" without all those spaces
        print("Classroom seeding complete                                     ")