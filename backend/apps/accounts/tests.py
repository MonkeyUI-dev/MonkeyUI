"""
Tests for the SheBuilds event registration endpoint.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.accounts.models import UserAPIKey


class EventRegisterViewTests(TestCase):
    """Test the event-register endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/accounts/event-register/'

    def test_event_register_creates_user_and_api_key(self):
        """POST /api/accounts/event-register/ should create a user with credentials and API key."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        # Check structure
        self.assertIn('credentials', data)
        self.assertIn('tokens', data)
        self.assertIn('user', data)

        creds = data['credentials']
        self.assertIn('email', creds)
        self.assertIn('password', creds)
        self.assertIn('api_key', creds)

        # Email should be in the expected format
        self.assertTrue(creds['email'].startswith('shebuilds-20260308-'))
        self.assertTrue(creds['email'].endswith('@monkeyui.com'))

        # API key should start with 'sk_'
        self.assertTrue(creds['api_key'].startswith('sk_'))

        # Tokens should be present
        self.assertIn('access', data['tokens'])
        self.assertIn('refresh', data['tokens'])

    def test_event_register_user_can_authenticate(self):
        """The generated credentials should allow login."""
        response = self.client.post(self.url)
        data = response.json()

        # Use the tokens to access a protected endpoint
        access_token = data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        me_response = self.client.get('/api/accounts/me/')
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.json()['user']['email'], data['credentials']['email'])

    def test_event_register_creates_unique_users(self):
        """Each call should create a different user."""
        response1 = self.client.post(self.url)
        response2 = self.client.post(self.url)

        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        email1 = response1.json()['credentials']['email']
        email2 = response2.json()['credentials']['email']
        self.assertNotEqual(email1, email2)

    def test_event_register_api_key_belongs_to_user(self):
        """The API key should be associated with the created user."""
        response = self.client.post(self.url)
        data = response.json()

        api_key = UserAPIKey.objects.get(key=data['credentials']['api_key'])
        self.assertEqual(api_key.user.email, data['credentials']['email'])
        self.assertEqual(api_key.name, 'SheBuilds Event Key')
