import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

@pytest.mark.django_db
def test_register_invalid_email_format(api_client):
    """Test registration with invalid email format."""
    url = reverse('register')
    response = api_client.post(url, {
        'email': 'invalid-email-format',
        'password': 'validpass123'
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.data

@pytest.mark.django_db
def test_verify_email_invalid_uid(api_client):
    """Test email verification with invalid UID."""
    url = reverse('verify-email', args=['invalid-uid', 'some-token'])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_302_FOUND
    assert 'verified=invalid' in response.url

@pytest.mark.django_db
def test_verify_email_invalid_token(api_client):
    """Test email verification with invalid token."""
    # Create a user
    user = User.objects.create_user(email='test@example.com', password='test123')

    # Use valid UID but invalid token
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    url = reverse('verify-email', args=[uid, 'invalid-token'])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_302_FOUND
    assert 'verified=expired' in response.url

@pytest.mark.django_db
def test_verify_email_already_used_token(api_client):
    """Test email verification with already used token."""
    # Create and verify a user
    user = User.objects.create_user(email='test@example.com', password='test123', is_active=False)

    # Get the token and verify once
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    url = reverse('verify-email', args=[uid, token])

    # First verification should work
    response1 = api_client.get(url)
    assert response1.status_code == status.HTTP_302_FOUND
    assert 'verified=true' in response1.url

    # Second verification with same token should still work (tokens don't expire after use)
    response2 = api_client.get(url)
    assert response2.status_code == status.HTTP_302_FOUND
    assert 'verified=true' in response2.url  # Already verified user

@pytest.mark.django_db
def test_change_password_same_as_old(authenticated_client):
    """Test changing password to the same value."""
    # Note: The current implementation doesn't prevent same password, it just validates strength
    url = reverse('change-password')
    response = authenticated_client.post(url, {
        'old_password': 'strongpassword123',  # Correct password from fixture
        'new_password': 'strongpassword123'  # Same as old - should succeed
    })
    assert response.status_code == status.HTTP_200_OK
    assert "Password changed successfully" in response.data["detail"]

@pytest.mark.django_db
def test_change_password_weak_new_password(authenticated_client):
    """Test changing to a weak new password."""
    url = reverse('change-password')
    response = authenticated_client.post(url, {
        'old_password': 'strongpassword123',  # Correct password from fixture
        'new_password': '123'  # Too short
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'error' in response.data  # Errors are returned in 'error' key

@pytest.mark.django_db
def test_user_profile_update_invalid_data(authenticated_client):
    """Test user profile update with invalid data."""
    url = reverse('user-profile')
    response = authenticated_client.put(url, {
        'first_name': '',  # Invalid: blank
        'last_name': 'Doe'
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'first_name' in response.data

@pytest.mark.django_db
def test_login_unverified_email(api_client):
    """Test login attempt with unverified email."""
    # Create unverified user
    User.objects.create_user(
        email='unverified@example.com',
        password='testpass123',
        is_active=False
    )

    url = reverse('token_obtain_pair')
    response = api_client.post(url, {
        'email': 'unverified@example.com',
        'password': 'testpass123'
    })
    # The view returns 401 for inactive accounts
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # The error message is generic for security reasons
    assert 'No active account found' in str(response.data)

@pytest.mark.django_db
def test_password_reset_request_nonexistent_email(api_client):
    """Test password reset request for non-existent email."""
    url = reverse('password-reset-request')
    response = api_client.post(url, {'email': 'nonexistent@example.com'})
    # Should still return 200 to avoid email enumeration
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_password_reset_confirm_invalid_uid(api_client):
    """Test password reset confirmation with invalid UID."""
    url = reverse('password-reset-confirm', args=['invalid-uid', 'some-token'])
    response = api_client.post(url, {
        'password': 'newpass123',
        'password_confirm': 'newpass123'
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST