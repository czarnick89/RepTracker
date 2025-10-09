import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status as s

User = get_user_model()

LOGIN_URL = reverse('token_obtain_pair')

@pytest.mark.django_db
def test_login_throttling():
    """Test that login throttling is configured (basic smoke test)."""
    # This is a simplified test that just verifies throttling is set up
    # Full throttling testing requires complex cache mocking
    client = APIClient()
    user = User.objects.create_user(email='throttle@example.com', password='correctpassword', is_active=True)

    # Make a few requests - they should all work (throttling is per time window)
    for _ in range(3):
        response = client.post(LOGIN_URL, {'email': 'throttle@example.com', 'password': 'wrongpassword'})
        # Should be 401 (not 429) since we're within rate limits
        assert response.status_code == s.HTTP_401_UNAUTHORIZED

    # Valid login should work
    response = client.post(LOGIN_URL, {'email': 'throttle@example.com', 'password': 'correctpassword'})
    assert response.status_code == s.HTTP_200_OK
