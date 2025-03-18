from django.core.management.base import BaseCommand
from faker import Faker
from random import randint, shuffle
from app.models import ( 
    Classroom,
    ClassroomStudent,
    ClassroomInvitation,
    GuestAccess,
    Quiz,
    TrueFalseQuestion,
    IntegerInputQuestion,
    MultipleChoiceQuestion,
    TextInputQuestion,
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
        self.generate_classroom_invite()
        self.generate_quizzes()

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
            correct_answer = integer_answer,
            time = 60,
            mark = 1
        )

        TrueFalseQuestion.objects.create(
            quiz = sample_quiz,
            question_text = f"The answer to this sample question is {str(integer_answer % 2 == 0)}",
            correct_answer = (integer_answer % 2 == 0),
            time = 60,
            mark = 1
        )

    """Classroom generating functions"""

    def generate_classroom(self):
        bob = User.objects.filter(email_address = "Bob.Tutor@example.org").first()
        john = User.objects.filter(email_address = "John.Doe@example.org").first()

        classroom = Classroom.objects.create(
            name = "Bob's Classroom",
            tutor = bob,
            description = "Hi, I'm Bob. I don't know any of you except John and Jane!"
        )
        print(f"Created {classroom.name}", end = '\r')

        ClassroomStudent.objects.create(classroom=classroom, student=john)

        classroom_count = ClassroomStudent.objects.filter(classroom=classroom).count()
        students = list(User.objects.filter(role=User.STUDENT)) 

        while classroom_count < Command.CLASSROOM_SIZE:
            if students: #check if students in empty
                student = students.pop()

                if not ClassroomStudent.objects.filter(classroom=classroom, student=student).exists():    
                    ClassroomStudent.objects.create(classroom = classroom, student = student)
                    print(f"Added {student.email_address} to {classroom.name}")
                    classroom_count += 1
            else:
                print("Students are less than required!")
                break

        #There's a bug here where it will type "Classroom seeding complete.org to Bob's Classroomsroom" without all those spaces
        print("Classroom seeding complete")
    
    def generate_classroom_invite(self):
        bob = User.objects.filter(email_address="Bob.Tutor@example.org").first()
        jane = User.objects.filter(email_address="Jane.Doe@example.org").first()
        classroom = Classroom.objects.filter(tutor=bob).first() 

        ClassroomInvitation.objects.create(classroom=classroom, student=jane, status="pending")
        print(f"Inivtation created for {jane.email_address} to {bob.first_name}'s Classroom")
    
    def generate_quizzes(self):
        bob = User.objects.filter(email_address="Bob.Tutor@example.org").first()
        
        self.generate_quiz_1(bob)

        
        self.generate_quiz_2(bob)

        
        self.generate_quiz_3(bob)

    def generate_quiz_1(self, tutor):
        quiz = Quiz.objects.create(
            name="Python Basics",
            subject="Example Quiz",
            difficulty="E",
            type="L",
            tutor=tutor
        )
        IntegerInputQuestion.objects.create(
            question_text="What is the output of `print(2 + 3 * 4)` in Python?",
            position=1,
            time=30,
            quiz=quiz,
            mark=1,
            correct_answer=14
        )

        TrueFalseQuestion.objects.create(
            question_text="Python is a low level programming language.",
            position=2,
            time=30,
            quiz=quiz,
            mark=1,
            correct_answer=False
        )

        MultipleChoiceQuestion.objects.create(
            question_text="Which of the following is used to take user input in Python?",
            position=3,
            time=30,
            quiz=quiz,
            mark=1,
            options={"A": "input()", "B": "scan()", "C": "get()", "D": "readline()"},
            correct_answer="A"
        )

        TextInputQuestion.objects.create(
            question_text="What keyword is used to define a class in Python?",
            position=4,
            time=30,
            quiz=quiz,
            mark=1,
            correct_answer="class"
        )

        print(f"Seeded {quiz.name} Quiz with 4 Questions")


    def generate_quiz_2(self, tutor):
        quiz = Quiz.objects.create(
            name="Arithmetic Test",
            subject="Example Quiz",
            difficulty="E",
            type="L",
            tutor=tutor
        )
        IntegerInputQuestion.objects.create(
            question_text="What is 1 + 1?",
            position=1,
            time=15,
            quiz=quiz,
            mark=1,
            correct_answer=2
        )

        IntegerInputQuestion.objects.create(
            question_text="What is 8 + 5?",
            position=2,
            time=15,
            quiz=quiz,
            mark=1,
            correct_answer=13
        )

        IntegerInputQuestion.objects.create(
            question_text="What is 12 - 4?",
            position=3,
            time=15,
            quiz=quiz,
            mark=1,
            correct_answer=8
        )

        IntegerInputQuestion.objects.create(
            question_text="What is the square of 6?",
            position=4,
            time=15,
            quiz=quiz,
            mark=2,
            correct_answer=36
        )

        IntegerInputQuestion.objects.create(
            question_text="What is 9 x 3?",
            position=5,
            time=15,
            quiz=quiz,
            mark=1,
            correct_answer=27
        )

        IntegerInputQuestion.objects.create(
            question_text="What is 18 ÷ 2?",
            position=6,
            time=15,
            quiz=quiz,
            mark=1,
            correct_answer=9
        )

        print(f"Seeded {quiz.name} Quiz with 6 Questions")

    def generate_quiz_3(self, tutor):
        quiz = Quiz.objects.create(
            name="Physics Basics",
            subject="Example Quiz",
            difficulty="E",
            type="L",
            tutor=tutor
        )

        MultipleChoiceQuestion.objects.create(
            question_text="What is the unit of force?",
            position=1,
            time=15,
            quiz=quiz,
            mark=1,
            options={"A": "Newton", "B": "Joule", "C": "Watt", "D": "Pascal"},
            correct_answer="A"
        )

        TrueFalseQuestion.objects.create(
            question_text="Sound can travel through a vacuum.",
            position=2,
            time=10,
            quiz=quiz,
            mark=1,
            correct_answer=False
        )

        IntegerInputQuestion.objects.create(
            question_text="What is the acceleration due to gravity on Earth (in m/s²)?",
            position=3,
            time=15,
            quiz=quiz,
            mark=2,
            correct_answer=9.8
        )

        
        MultipleChoiceQuestion.objects.create(
            question_text="Which of these is a form of potential energy?",
            position=4,
            time=15,
            quiz=quiz,
            mark=1,
            options={"A": "Kinetic Energy", "B": "Thermal Energy", "C": "Gravitational Energy", "D": "Light Energy"},
            correct_answer="C"
        )

        TextInputQuestion.objects.create(
            question_text="Which electrical quantity is measured in amps?",
            position=5,
            time=15,
            quiz=quiz,
            mark=1,
            correct_answer = "current"
        )

        print(f"Seeded {quiz.name} Quiz with 5 Questions")