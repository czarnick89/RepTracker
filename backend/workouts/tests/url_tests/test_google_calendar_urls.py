import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestGoogleCalendarURLs:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='user@example.com', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_google_calendar_auth_start_url(self):
        """Test that google_calendar_auth_start URL resolves correctly."""
        url = reverse('google_calendar_auth_start')
        assert url == '/api/v1/workouts/google-calendar/auth-start/'

        # Test GET request
        response = self.client.get(url)
        # Should redirect or return appropriate response
        assert response.status_code in [302, 401, 403]  # Redirect or auth error

    def test_google_calendar_oauth2callback_url(self):
        """Test that google_calendar_oauth2callback URL resolves correctly."""
        url = reverse('google_calendar_oauth2callback')
        assert url == '/api/v1/workouts/google-calendar/oauth2callback/'

        # Test POST request structure
        response = self.client.post(url, {})
        # Should return appropriate response
        assert response.status_code in [400, 401, 404]  # Valid responses from the view

    def test_add_workout_to_calendar_url(self):
        """Test that add_workout_to_calendar URL resolves correctly."""
        url = reverse('add_workout_to_calendar')
        assert url == '/api/v1/workouts/google-calendar/create-event/'

        # Test POST request structure
        response = self.client.post(url, {})
        # Should return appropriate response
        assert response.status_code in [400, 401]  # Valid responses from the view

    def test_google_calendar_status_url(self):
        """Test that google_calendar_status URL resolves correctly."""
        url = reverse('google_calendar_status')
        assert url == '/api/v1/workouts/google-calendar/status/'

        # Test GET request
        response = self.client.get(url)
        # Should return status
        assert response.status_code in [200, 401]  # Valid responses from the view

    def test_google_calendar_disconnect_url(self):
        """Test that google_calendar_disconnect URL resolves correctly."""
        url = reverse('google_calendar_disconnect')
        assert url == '/api/v1/workouts/google-calendar/disconnect/'

        # Test POST request
        response = self.client.post(url)
        # Should return appropriate response
        assert response.status_code in [200, 401]  # Valid responses from the view

    def test_google_calendar_views_require_authentication(self):
        """Test that Google Calendar views require authentication (except callback)."""
        self.client.force_authenticate(user=None)

        urls = [
            reverse('google_calendar_auth_start'),
            reverse('add_workout_to_calendar'),
            reverse('google_calendar_status'),
            reverse('google_calendar_disconnect'),
        ]

        for url in urls:
            if 'status' in url:
                response = self.client.get(url)
            else:
                response = self.client.post(url)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"URL {url} should require auth"

    def test_google_calendar_oauth2callback_allows_any(self):
        """Test that OAuth callback allows unauthenticated requests."""
        self.client.force_authenticate(user=None)
        url = reverse('google_calendar_oauth2callback')
        response = self.client.post(url, {})
        # Should not return 401 (authentication not required for callback)
        assert response.status_code != status.HTTP_401_UNAUTHORIZED