import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_resend_verification_email_success(api_client):
    """Test resending verification email to an inactive user."""
    # Create an inactive user
    user = User.objects.create_user(
        email='inactive@example.com',
        password='testpass123',
        is_active=False
    )

    url = reverse('resend-verification')
    response = api_client.post(url, {'email': 'inactive@example.com'})

    assert response.status_code == status.HTTP_200_OK
    assert "Verification email resent" in response.data["detail"]


@pytest.mark.django_db
def test_resend_verification_email_already_active(api_client):
    """Test resending verification email to an already active user."""
    # Create an active user
    user = User.objects.create_user(
        email='active@example.com',
        password='testpass123',
        is_active=True
    )

    url = reverse('resend-verification')
    response = api_client.post(url, {'email': 'active@example.com'})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already verified" in response.data["detail"].lower()


@pytest.mark.django_db
def test_resend_verification_email_nonexistent_user(api_client):
    """Test resending verification email to a non-existent user."""
    url = reverse('resend-verification')
    response = api_client.post(url, {'email': 'nonexistent@example.com'})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "does not exist" in response.data["email"].lower()


@pytest.mark.django_db
def test_resend_verification_email_missing_email(api_client):
    """Test resending verification email with missing email field."""
    url = reverse('resend-verification')
    response = api_client.post(url, {})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "required" in response.data["email"].lower()


@pytest.mark.django_db
def test_resend_verification_email_case_insensitive(api_client):
    """Test resending verification email with different case email."""
    # Create user with lowercase email
    user = User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        is_active=False
    )

    url = reverse('resend-verification')
    # Try with uppercase email
    response = api_client.post(url, {'email': 'TEST@EXAMPLE.COM'})

    assert response.status_code == status.HTTP_200_OK
    assert "Verification email resent" in response.data["detail"]