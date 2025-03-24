from channels.testing import WebsocketCommunicator
from django.test import TestCase
from app.consumers.lobby_consumer import LobbyConsumer
from app.models import Room, RoomParticipant, User, GuestAccess
from channels.db import database_sync_to_async as sync_to_async
import json

class LobbyConsumerTests(TestCase):
    async def test_connect(self):
        communicator = WebsocketCommunicator(LobbyConsumer.as_asgi(), "/ws/lobby/ABCD1234/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_disconnect(self):
        communicator = WebsocketCommunicator(LobbyConsumer.as_asgi(), "/ws/lobby/ABCD1234/")
        await communicator.connect()
        connected, _ = await communicator.disconnect()

        self.assertFalse(connected)

    async def test_participants_update(self):
        room = sync_to_async(Room.objects.create)(join_code="ABCD1234", name="My Room")
        user = sync_to_async(User.objects.create)(first_name="John", last_name="Doe", email_address="johndoe@example.org")
        guest = sync_to_async(GuestAccess.objects.create)(session_id="abcdefghijkl")
        user_participant = sync_to_async(RoomParticipant.objects.create)(room=room, user=user)
        guest_participant = sync_to_async(RoomParticipant.objects.create)(room=room, guest_access=guest)
        communicator = WebsocketCommunicator(LobbyConsumer.as_asgi(), "/ws/lobby/ABCD1234/")

        await communicator.connect()

        await communicator.send_json_to({
            "action": "update"
        })

        response = await communicator.receive_json_from()

        self.assertEqual(response, {
            "type": "participants_update",
            "participants": ["johndoe@example.org", "Guest (abcdefgh)"]
        })

        await communicator.disconnect()

    async def test_quiz_started(self):
        room = sync_to_async(Room.objects.create)(join_code="ABCD1234", name="My Room")
        communicator = WebsocketCommunicator(LobbyConsumer.as_asgi(), "/ws/lobby/ABCD1234/")

        await communicator.connect()

        await communicator.send_json_to({
            "action": "quiz_started",
            "student_quiz_url": "student_quiz_url",
            "tutor_quiz_url": "tutor_quiz_url"
        })

        response = await communicator.receive_json_from()

        self.assertEqual(response, {
            "action": "quiz_started",
            "student_quiz_url": "student_quiz_url",
            "tutor_quiz_url": "tutor_quiz_url"
        })

        await communicator.disconnect()
