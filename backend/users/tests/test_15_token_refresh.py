import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

@pytest.mark.django_db
def test_token_refresh_success(api_client):
    """Test successful token refresh with valid refresh cookie."""
    # Create and login user to get initial tokens
    user = User.objects.create_user(
        email='refresh@example.com',
        password='testpass123',
        is_active=True
    )

    login_url = reverse('token_obtain_pair')
    login_response = api_client.post(login_url, {
        'email': 'refresh@example.com',
        'password': 'testpass123'
    })
    assert login_response.status_code == status.HTTP_200_OK

    # Extract refresh token from login response
    refresh_token = login_response.cookies['refresh_token'].value

    # Now test refresh with the refresh token in cookie
    refresh_url = reverse('token_refresh')
    api_client.cookies['refresh_token'] = refresh_token

    refresh_response = api_client.post(refresh_url)

    assert refresh_response.status_code == status.HTTP_200_OK
    assert "Token refreshed successfully" in refresh_response.data["detail"]
    assert "access_token" in refresh_response.cookies
    # Should get a new refresh token due to rotation
    assert "refresh_token" in refresh_response.cookies


@pytest.mark.django_db
def test_token_refresh_missing_cookie(api_client):
    """Test token refresh with missing refresh cookie."""
    refresh_url = reverse('token_refresh')
    response = api_client.post(refresh_url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "No refresh token cookie found" in response.data["error"]


@pytest.mark.django_db
def test_token_refresh_invalid_token(api_client):
    """Test token refresh with invalid refresh token."""
    refresh_url = reverse('token_refresh')
    api_client.cookies['refresh_token'] = 'invalid.token.here'

    response = api_client.post(refresh_url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid refresh token" in response.data["error"]


@pytest.mark.django_db
def test_token_refresh_blacklisted_token(api_client):
    """Test token refresh with blacklisted refresh token."""
    # Create user and get refresh token
    user = User.objects.create_user(
        email='blacklist@example.com',
        password='testpass123',
        is_active=True
    )

    refresh = RefreshToken.for_user(user)
    refresh_token_str = str(refresh)

    # Blacklist the token
    refresh.blacklist()

    # Try to refresh with blacklisted token
    refresh_url = reverse('token_refresh')
    api_client.cookies['refresh_token'] = refresh_token_str

    response = api_client.post(refresh_url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid refresh token" in response.data["error"]