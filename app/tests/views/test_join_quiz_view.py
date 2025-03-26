from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from app.models import Room

class JoinQuizTests(TestCase):
    
    def setUp(self):
        # Create a Room instance to test with
        self.room = Room.objects.create(join_code='VALID1234')

    def test_valid_join_code(self):
        """Test that a valid join code redirects to the lobby page."""
        response = self.client.post(reverse('join_quiz'), {'join_code': 'VALID1234'})

        # Ensure redirect to lobby with the correct code
        self.assertRedirects(response, reverse('lobby', kwargs={'join_code': 'VALID1234'}))

    def test_invalid_join_code(self):
        """Test that an invalid join code shows an error message."""
        response = self.client.post(reverse('join_quiz'), {'join_code': 'INVALIDCODE'})

        # Check if an error message is displayed
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid code. Please try again.')

        # Ensure the user is still on the join page
        self.assertTemplateUsed(response, 'join.html')

    def test_get_request_renders_join_page(self):
        """Test that a GET request renders the join.html page."""
        response = self.client.get(reverse('join_quiz'))
        self.assertTemplateUsed(response, 'join.html')