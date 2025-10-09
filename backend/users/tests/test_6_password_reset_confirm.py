import pytest
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

@pytest.mark.django_db
class TestPasswordResetConfirm:

    def test_successful_reset(self, api_client, verified_user):
        uidb64 = urlsafe_base64_encode(force_bytes(verified_user.pk))
        token = default_token_generator.make_token(verified_user)

        url = reverse('password-reset-confirm', args=[uidb64, token])
        data = {"password": "NewStrongPass123"}

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "Password has been reset successfully." in response.data["detail"]

        # Confirm password was actually changed
        verified_user.refresh_from_db()
        assert verified_user.check_password("NewStrongPass123")

    def test_missing_password(self, api_client, verified_user):
        uidb64 = urlsafe_base64_encode(force_bytes(verified_user.pk))
        token = default_token_generator.make_token(verified_user)

        url = reverse('password-reset-confirm', args=[uidb64, token])
        response = api_client.post(url, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Password is required." in response.data["error"]

    def test_invalid_token(self, api_client, verified_user):
        uidb64 = urlsafe_base64_encode(force_bytes(verified_user.pk))
        invalid_token = "invalid-token"

        url = url = reverse('password-reset-confirm', args=[uidb64, invalid_token])
        data = {"password": "NewStrongPass123"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid or expired token." in response.data["error"]

    def test_invalid_uid(self, api_client):
        uidb64 = "invalid-uid"
        token = "any-token"
        url = reverse('password-reset-confirm', args=[uidb64, token])
        data = {"password": "NewStrongPass123"}

        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid link." in response.data["error"]

    def test_password_too_weak(self, api_client, verified_user):
        uidb64 = urlsafe_base64_encode(force_bytes(verified_user.pk))
        token = default_token_generator.make_token(verified_user)

        url = reverse('password-reset-confirm', args=[uidb64, token])
        data = {"password": "123"}

        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert isinstance(response.data["error"], list)
