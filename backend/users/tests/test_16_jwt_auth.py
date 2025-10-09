import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

@pytest.mark.django_db
def test_jwt_authentication_valid_token(api_client):
    """Test JWT authentication with valid access token in cookie."""
    # Create user and generate access token
    user = User.objects.create_user(
        email='auth@example.com',
        password='testpass123',
        is_active=True
    )
    access_token = AccessToken.for_user(user)

    # Set access token in cookie
    api_client.cookies['access_token'] = str(access_token)

    # Try to access a protected endpoint
    profile_url = reverse('user-profile')
    response = api_client.get(profile_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == 'auth@example.com'


@pytest.mark.django_db
def test_jwt_authentication_missing_token(api_client):
    """Test JWT authentication with missing access token cookie."""
    # Try to access protected endpoint without token
    profile_url = reverse('user-profile')
    response = api_client.get(profile_url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_jwt_authentication_invalid_token(api_client):
    """Test JWT authentication with invalid access token."""
    # Set invalid token in cookie
    api_client.cookies['access_token'] = 'invalid.token.here'

    # Try to access protected endpoint
    profile_url = reverse('user-profile')
    response = api_client.get(profile_url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_jwt_authentication_expired_token(api_client):
    """Test JWT authentication with expired access token."""
    # Create user and generate expired access token
    user = User.objects.create_user(
        email='expired@example.com',
        password='testpass123',
        is_active=True
    )

    # Create token that's already expired (set lifetime to -1 second)
    import time
    from datetime import datetime, timedelta
    from django.utils import timezone

    access_token = AccessToken.for_user(user)
    # Manually set expiration to past
    access_token.set_exp(lifetime=timedelta(seconds=-1))

    # Set expired token in cookie
    api_client.cookies['access_token'] = str(access_token)

    # Try to access protected endpoint
    profile_url = reverse('user-profile')
    response = api_client.get(profile_url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_jwt_authentication_malformed_token(api_client):
    """Test JWT authentication with malformed token."""
    # Set malformed token in cookie
    api_client.cookies['access_token'] = 'not.a.jwt.token'

    # Try to access protected endpoint
    profile_url = reverse('user-profile')
    response = api_client.get(profile_url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED