import pytest
from django.urls import reverse
from django.test import RequestFactory
from rest_framework.test import APIClient
from unittest.mock import patch, Mock
from users.models import User

@pytest.mark.django_db
class TestGoogleCalendarViews:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@example.com', password='password123')
        self.client.force_authenticate(user=self.user)
        self.factory = RequestFactory()

    def test_google_calendar_auth_start_redirects(self):
        """Test that auth start redirects to Google OAuth."""
        url = reverse('google_calendar_auth_start')
        response = self.client.get(url)
        assert response.status_code == 302  # Redirect
        assert 'accounts.google.com' in response.url

    def test_google_calendar_auth_start_requires_auth(self):
        """Test that auth start requires authentication."""
        self.client.force_authenticate(user=None)
        url = reverse('google_calendar_auth_start')
        response = self.client.get(url)
        assert response.status_code == 401

    @patch('workouts.views.Flow.from_client_config')
    def test_google_calendar_oauth_callback_success(self, mock_flow):
        """Test successful OAuth callback."""
        # Mock the flow
        mock_flow_instance = Mock()
        mock_flow_instance.fetch_token.return_value = None
        mock_credentials = Mock()
        mock_credentials.token = 'access_token_123'
        mock_credentials.refresh_token = 'refresh_token_456'
        mock_credentials.expiry = None
        mock_flow_instance.credentials = mock_credentials
        mock_flow.return_value = mock_flow_instance

        url = reverse('google_calendar_oauth2callback')

        # Set up session data
        session = self.client.session
        session['google_oauth_state'] = 'test_state'
        session['google_oauth_user_id'] = self.user.id
        session.save()

        data = {
            'code': 'auth_code_123',
            'state': 'test_state'
        }

        response = self.client.post(url, data, format='json')
        assert response.status_code == 200
        assert "linked successfully" in response.data["detail"]

        # Check that tokens were saved
        self.user.refresh_from_db()
        assert self.user.google_access_token == 'access_token_123'
        assert self.user.google_refresh_token == 'refresh_token_456'

    def test_google_calendar_oauth_callback_missing_code(self):
        """Test OAuth callback with missing code."""
        url = reverse('google_calendar_oauth2callback')
        response = self.client.post(url, {}, format='json')
        assert response.status_code == 400
        assert "Missing code or state" in response.data["detail"]

    def test_google_calendar_oauth_callback_invalid_state(self):
        """Test OAuth callback with invalid state."""
        url = reverse('google_calendar_oauth2callback')

        # Set up session with different state
        session = self.client.session
        session['google_oauth_state'] = 'different_state'
        session['google_oauth_user_id'] = self.user.id
        session.save()

        data = {
            'code': 'auth_code_123',
            'state': 'wrong_state'
        }

        response = self.client.post(url, data, format='json')
        assert response.status_code == 400
        assert "Invalid state" in response.data["detail"]

    @patch('workouts.views.get_google_calendar_service')
    def test_add_workout_to_calendar_success(self, mock_get_service):
        """Test successfully adding workout to calendar."""
        mock_service = Mock()
        mock_event = {'id': 'event_123'}
        mock_service.events.return_value.insert.return_value.execute.return_value = mock_event
        mock_get_service.return_value = mock_service

        url = reverse('add_workout_to_calendar')
        data = {
            'summary': 'Test Workout',
            'start_time': '2025-01-01T10:00:00Z',
            'end_time': '2025-01-01T11:00:00Z'
        }

        response = self.client.post(url, data, format='json')
        assert response.status_code == 200
        assert response.data['event_id'] == 'event_123'

    @patch('workouts.views.get_google_calendar_service')
    def test_add_workout_to_calendar_not_connected(self, mock_get_service):
        """Test adding workout when not connected to Google Calendar."""
        mock_get_service.return_value = None

        url = reverse('add_workout_to_calendar')
        data = {
            'summary': 'Test Workout',
            'start_time': '2025-01-01T10:00:00Z',
            'end_time': '2025-01-01T11:00:00Z'
        }

        response = self.client.post(url, data, format='json')
        assert response.status_code == 401
        assert "authorization required" in response.data["detail"]

    @patch('workouts.views.get_google_calendar_service')
    def test_google_calendar_status_connected(self, mock_get_service):
        """Test calendar status when connected."""
        mock_get_service.return_value = Mock()
        url = reverse('google_calendar_status')
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data['connected'] is True
        assert response['Cache-Control'] == 'no-store, no-cache, must-revalidate, max-age=0'

    @patch('workouts.views.get_google_calendar_service')
    def test_google_calendar_status_not_connected(self, mock_get_service):
        """Test calendar status when not connected."""
        mock_get_service.return_value = None
        url = reverse('google_calendar_status')
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data['connected'] is False

    @patch('workouts.views.requests.post')
    def test_google_calendar_disconnect_success(self, mock_post):
        """Test successfully disconnecting Google Calendar."""
        # Set up user with tokens
        self.user.google_access_token = 'token_123'
        self.user.google_refresh_token = 'refresh_456'
        self.user.save()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        url = reverse('google_calendar_disconnect')
        response = self.client.post(url)

        assert response.status_code == 200
        assert "disconnected" in response.data["message"]

        # Check that tokens were cleared
        self.user.refresh_from_db()
        assert self.user.google_access_token is None
        assert self.user.google_refresh_token is None
        assert self.user.google_token_expiry is None

    def test_google_calendar_views_require_auth(self):
        """Test that all Google Calendar views require authentication."""
        self.client.force_authenticate(user=None)

        urls = [
            reverse('google_calendar_auth_start'),
            reverse('add_workout_to_calendar'),
            reverse('google_calendar_status'),
            reverse('google_calendar_disconnect'),
        ]

        for url in urls:
            if url == reverse('google_calendar_oauth2callback'):
                continue  # This one allows any
            response = self.client.get(url) if 'status' in url else self.client.post(url)
            assert response.status_code == 401, f"URL {url} should require auth"