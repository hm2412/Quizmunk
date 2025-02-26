from django.core.management.base import BaseCommand
from app.models import Room, RoomParticipant, User, GuestAccess
import uuid

'''Seeder for testing the live quiz leaderboard ordering prior to WebSocket connections'''

class Command(BaseCommand):
    help = 'Seeds the database with test data for leaderboard'

    def handle(self, *args, **kwargs):
        # Create a test room
        room1, _ = Room.objects.get_or_create(name="Room 1")
        room2, _ = Room.objects.get_or_create(name="Room 2")

        # Create test users
        user1 = User.objects.create_user(email_address='alice@example.com', first_name='Alice', last_name='Smith', role=User.STUDENT)
        user2 = User.objects.create_user(email_address='bob@example.com', first_name='Bob', last_name='Jobs', role=User.STUDENT)
        user3 = User.objects.create_user(email_address='charlie@example.com', first_name='Charlie', last_name='Sonner', role=User.STUDENT)
        user4 = User.objects.create_user(email_address='david@example.com', first_name='David', last_name='Attenborough', role=User.STUDENT)
        user5 = User.objects.create_user(email_address='eve@example.com', first_name='Eve', last_name='Adan', role=User.STUDENT)
        user6 = User.objects.create_user(email_address='frank@example.com', first_name='Frank', last_name='Sinatra', role=User.STUDENT)
        user7 = User.objects.create_user(email_address='grace@example.com', first_name='Grace', last_name='Kelly', role=User.STUDENT)

        # Create guest access records
        guest1 = GuestAccess.objects.create(classroom_code="ABC123", session_id=str(uuid.uuid4()))
        guest2 = GuestAccess.objects.create(classroom_code="XYZ789", session_id=str(uuid.uuid4()))

        # Create RoomParticipants (users)
        RoomParticipant.objects.create(room=room1, guest_access=guest1, score=35)
        RoomParticipant.objects.create(room=room1, user=user1, score=50)
        RoomParticipant.objects.create(room=room1, user=user2, score=45)
        RoomParticipant.objects.create(room=room1, user=user4, score=65)
        RoomParticipant.objects.create(room=room1, user=user5, score=55)

        # Create RoomParticipants for Room 2
        RoomParticipant.objects.create(room=room2, guest_access=guest2, score=30)
        RoomParticipant.objects.create(room=room2, user=user3, score=40)
        RoomParticipant.objects.create(room=room2, user=user6, score=25)
        RoomParticipant.objects.create(room=room2, user=user7, score=45)


        self.stdout.write(self.style.SUCCESS("Successfully seeded test data"))
