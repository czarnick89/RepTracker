import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status as s
from time import sleep

User = get_user_model()

LOGIN_URL = reverse('token_obtain_pair')

@pytest.mark.django_db
def test_login_throttling(settings):
    # Override throttle rate for faster testing
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['login'] = '10/minute'

    client = APIClient()
    # Use a specific IP to avoid interference with other tests
    client.defaults['REMOTE_ADDR'] = '192.168.1.100'

    # Create a valid user
    user = User.objects.create_user(email='throttle@example.com', password='correctpassword', is_active=True)

    # Make 10 invalid login attempts
    for _ in range(10):
        response = client.post(LOGIN_URL, {'email': 'throttle@example.com', 'password': 'wrongpassword'})
        assert response.status_code == s.HTTP_401_UNAUTHORIZED  # Unauthorized

    # 11th attempt should be throttled
    response = client.post(LOGIN_URL, {'email': 'throttle@example.com', 'password': 'wrongpassword'})
    assert response.status_code == s.HTTP_429_TOO_MANY_REQUESTS  # Throttled
    assert "throttled" in response.data["detail"].lower()

    # Wait 61 seconds to bypass throttle window
    sleep(61)

    # Valid login attempt after cooldown should succeed
    response = client.post(LOGIN_URL, {'email': 'throttle@example.com', 'password': 'correctpassword'})
    assert response.status_code == s.HTTP_200_OK
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies
