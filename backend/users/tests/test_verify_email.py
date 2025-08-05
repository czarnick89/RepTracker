import pytest
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from users.models import User

@pytest.mark.django_db
def test_verify_email_success(client):
    # Create inactive user (simulate registration but unverified)
    user = User.objects.create_user(email="test@example.com", password="password123", is_active=False)

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    url = reverse("verify-email", args=[uid, token])
    response = client.get(url)

    user.refresh_from_db()
    assert response.status_code == 200
    assert user.is_active is True
    assert "email verified" in response.data.get("detail", "").lower()

@pytest.mark.django_db
def test_verify_email_invalid_token(client):
    user = User.objects.create_user(email="test2@example.com", password="password123", is_active=False)

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    invalid_token = "invalid-token"

    url = reverse("verify-email", args=[uid, invalid_token])
    response = client.get(url)

    user.refresh_from_db()
    assert response.status_code == 400
    assert user.is_active is False
    assert "invalid" in response.data.get("error", "").lower()
