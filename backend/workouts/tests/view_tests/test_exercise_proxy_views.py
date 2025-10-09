import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from unittest.mock import patch, Mock
from users.models import User

@pytest.mark.django_db
class TestExerciseByNameProxy:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@example.com', password='password123')
        self.client.force_authenticate(user=self.user)

    def test_successful_exercise_fetch(self):
        """Test successful fetching of exercise data by name."""
        url = reverse('exercise_by_name_proxy')
        mock_response_data = [{"name": "push-up", "id": "001"}]

        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response

            response = self.client.get(url, {'name': 'push-up'})

            assert response.status_code == 200
            assert response.data == mock_response_data
            mock_get.assert_called_once()

    def test_missing_name_parameter(self):
        """Test request without name parameter returns 400."""
        url = reverse('exercise_by_name_proxy')
        response = self.client.get(url)
        assert response.status_code == 400
        assert "Missing 'name' parameter" in response.data["detail"]

    def test_external_api_error(self):
        """Test handling of external API errors."""
        url = reverse('exercise_by_name_proxy')

        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            response = self.client.get(url, {'name': 'nonexistent'})

            assert response.status_code == 404
            assert "Failed to fetch exercise" in response.data["detail"]

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access the proxy."""
        self.client.force_authenticate(user=None)
        url = reverse('exercise_by_name_proxy')
        response = self.client.get(url, {'name': 'push-up'})
        assert response.status_code == 401

    def test_throttling_applied(self):
        """Test that throttling is applied to the view."""
        url = reverse('exercise_by_name_proxy')

        # Make multiple requests quickly
        responses = []
        for _ in range(5):
            response = self.client.get(url, {'name': 'push-up'})
            responses.append(response.status_code)

        # At least one should be throttled (429)
        assert 429 in responses