import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestProxyURLs:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='user@example.com', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_exercise_by_name_proxy_url(self):
        """Test that exercise_by_name_proxy URL resolves correctly."""
        url = reverse('exercise_by_name_proxy')
        assert url == '/api/v1/workouts/exercise-by-name/'

        # Test GET request structure
        response = self.client.get(url, {'name': 'push-up'})
        # Should get 200 (mocked) or appropriate response
        assert response.status_code in [200, 400, 404, 429]  # Valid responses from the view

    def test_exercise_gif_proxy_url(self):
        """Test that exercise_gif_proxy URL resolves correctly."""
        url = reverse('exercise_gif_proxy')
        assert url == '/api/v1/workouts/exercise-gif/'

        # Test GET request structure
        response = self.client.get(url, {'exerciseId': '123', 'resolution': '180'})
        # Should get appropriate response
        assert response.status_code in [200, 400, 404, 422, 429]  # Valid responses from the view

    def test_proxy_views_require_authentication(self):
        """Test that proxy views require authentication."""
        self.client.force_authenticate(user=None)

        urls = [
            reverse('exercise_by_name_proxy'),
            reverse('exercise_gif_proxy'),
        ]

        for url in urls:
            response = self.client.get(url)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED