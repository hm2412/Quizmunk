from django.core.management.base import BaseCommand
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

class Command(BaseCommand):

    def handle(self, *args, **options):
        """Unseed the database."""

        User.objects.filter(is_staff=False).delete()
        Classroom.objects.all().delete()
        ClassroomStudent.objects.all().delete()
        GuestAccess.objects.all().delete()
        Quiz.objects.all().delete()
        TrueFalseQuestion.objects.all().delete()
        IntegerInputQuestion.objects.all().delete()
        Room.objects.all().delete()
        RoomParticipant.objects.all().delete()
