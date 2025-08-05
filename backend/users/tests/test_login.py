import pytest
from django.urls import reverse
from users.models import User

@pytest.mark.django_db
def test_login_success(client):
    # Create active user
    user = User.objects.create_user(email="loginuser@example.com", password="password123", is_active=True)

    url = reverse("login")
    data = {"email": user.email, "password": "password123"}  # 'username' is the expected key by DRF's token auth

    response = client.post(url, data)

    assert response.status_code == 200
    assert "token" in response.data
    assert len(response.data["token"]) > 0

@pytest.mark.django_db
def test_login_fail(client):
    user = User.objects.create_user(email="loginfail@example.com", password="password123", is_active=True)

    url = reverse("login")
    data = {"username": user.email, "password": "wrongpassword"}

    response = client.post(url, data)

    assert response.status_code == 401
    assert "error" in response.data
    assert response.data["error"] == "Invalid credentials."
