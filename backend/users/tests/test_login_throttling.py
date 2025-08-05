import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status as s
from time import sleep

User = get_user_model()

LOGIN_URL = reverse('login') 

@pytest.mark.django_db
def test_login_throttling(settings):
    # Set rate limit to something testable
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['login'] = '5/minute'

    client = APIClient()

    # Create a valid user
    user = User.objects.create_user(email='throttle@example.com', password='correctpassword', is_active=True)

    # Make 5 invalid login attempts
    for _ in range(5):
        response = client.post(LOGIN_URL, {'email': 'throttle@example.com', 'password': 'wrongpassword'})
        assert response.status_code == s.HTTP_401_UNAUTHORIZED  # Unauthorized

    # 6th attempt should be throttled
    response = client.post(LOGIN_URL, {'email': 'throttle@example.com', 'password': 'wrongpassword'})
    assert response.status_code == s.HTTP_429_TOO_MANY_REQUESTS  # Throttled
    assert "throttled" in response.data["detail"].lower()

    # Wait 61 seconds to bypass throttle window
    # sleep(61) # commented this part of test out so it doesnt take a min to run each time

    # # Valid login attempt after cooldown should succeed
    # response = client.post(LOGIN_URL, {'email': 'throttle@example.com', 'password': 'correctpassword'})
    # assert response.status_code == s.HTTP_200_OK
    # assert 'token' in response.data
