import pytest
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_full_user_lifecycle():
    client = APIClient()

    # 1) Register user (inactive)
    register_url = reverse("register")
    user_data = {"email": "lifecycle@example.com", "password": "strongpass123"}
    register_response = client.post(register_url, user_data)
    assert register_response.status_code == 201
    assert "Check your email" in register_response.data["detail"]

    user = User.objects.get(email=user_data["email"])
    assert user.is_active is False

    # 2) Verify email to activate (now redirects instead of JSON)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verify_url = reverse("verify-email", args=[uid, token])
    verify_response = client.get(verify_url)
    assert verify_response.status_code == 302  # Redirect
    assert "verified=true" in verify_response.url

    user.refresh_from_db()
    assert user.is_active is True

    # 3) Login to get JWT cookies
    login_url = reverse("token_obtain_pair")
    login_data = {"email": user.email, "password": user_data["password"]}
    login_response = client.post(login_url, login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.cookies
    assert "refresh_token" in login_response.cookies

    # 4) Logout to blacklist JWT and clear cookies
    logout_url = reverse("logout")
    logout_response = client.post(logout_url)
    assert logout_response.status_code == 200
    assert "logged out" in logout_response.data["detail"].lower()

    # Cookies should be cleared (delete_cookie sets them to empty values)
    assert logout_response.cookies["access_token"].value == ""
    assert logout_response.cookies["refresh_token"].value == ""
