from django.core.management.base import BaseCommand
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

class Command(BaseCommand):

    def handle(self, *args, **options):
        """Unseed the database."""

        User.objects.all().delete()
        Classroom.objects.all().delete()
        ClassroomStudent.objects.all().delete()
        ClassroomInvitation.objects.all().delete()
        GuestAccess.objects.all().delete()
        Quiz.objects.all().delete()
        TrueFalseQuestion.objects.all().delete()
        IntegerInputQuestion.objects.all().delete()
        MultipleChoiceQuestion.objects.all().delete(),
        TextInputQuestion.objects.all().delete(),
        Room.objects.all().delete()
        RoomParticipant.objects.all().delete()
