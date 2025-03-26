from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase
from app.consumers.lobby_consumer import LobbyConsumer
from app.models import Room, RoomParticipant, User, GuestAccess
from channels.db import database_sync_to_async as sync_to_async
import json

class LobbyConsumerTests(TransactionTestCase):
    def setUp(self):
        self.room = Room.objects.create(join_code="ABCD1234", name="My Room")
        self.student = User.objects.create(first_name="John", last_name="Doe", email_address="johndoe@example.org")
        self.teacher = User.objects.create(first_name="Alice", last_name="Tutor", email_address="alicetutor@example.org")
        self.guest = GuestAccess.objects.create(session_id="abcdefghijkl")
        self.user_participant = RoomParticipant.objects.create(room=self.room, user=self.student)
        self.guest_participant = RoomParticipant.objects.create(room=self.room, guest_access=self.guest)

    async def test_student_connect(self):
        communicator = WebsocketCommunicator(LobbyConsumer.as_asgi(), "/ws/lobby/ABCD1234/")
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}
        communicator.scope['user'] = self.student
        session = await sync_to_async(lambda: dict(self.client.session))()
        communicator.scope['session'] = session
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_guest_connect(self):
        communicator = WebsocketCommunicator(LobbyConsumer.as_asgi(), "/ws/lobby/ABCD1234/")
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}
        session = await sync_to_async(lambda: dict(self.client.session))()
        communicator.scope['session'] = session
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_teacher_connect(self):
        communicator = WebsocketCommunicator(LobbyConsumer.as_asgi(), "/ws/lobby/ABCD1234/")
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}
        communicator.scope['user'] = self.teacher
        session = await sync_to_async(lambda: dict(self.client.session))()
        communicator.scope['session'] = session
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_valid_receive(self):
        communicator = WebsocketCommunicator(LobbyConsumer.as_asgi(), "/ws/lobby/ABCD1234/")
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}
        communicator.scope['user'] = self.teacher
        session = await sync_to_async(lambda: dict(self.client.session))()
        communicator.scope['session'] = session
        await communicator.connect()

        await communicator.send_json_to({
            "action": "quiz_started",
            "student_quiz_url": "/student/live-quiz/ABCD1234/",
            "tutor_quiz_url": "/live-quiz/1/ABCD1234/"
        })

        response = None
        while True:
            response = await communicator.receive_json_from()
            if response.get("type") == "quiz_started":
                break

        self.assertEqual(response["type"], "quiz_started")

        await communicator.disconnect()

    async def test_invalid_receive(self):
        communicator = WebsocketCommunicator(LobbyConsumer.as_asgi(), "/ws/lobby/ABCD1234/")
        communicator.scope['url_route'] = {'kwargs': {'join_code': 'ABCD1234'}}
        communicator.scope['user'] = self.teacher
        session = await sync_to_async(lambda: dict(self.client.session))()
        communicator.scope['session'] = session
        await communicator.connect()

        await communicator.send_json_to({
            "action": "Invalid action"
        })

        response = None
        while True:
            response = await communicator.receive_json_from()
            if response.get("error") == "Unknown action in lobby":
                break

        self.assertEqual(response, {"error": "Unknown action in lobby"})

        await communicator.disconnect()
