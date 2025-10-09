import pytest
from django.urls import reverse
from users.models import User

@pytest.mark.django_db
def test_login_success(client):
    # Create active user
    user = User.objects.create_user(email="loginuser@example.com", password="password123", is_active=True)

    url = reverse("token_obtain_pair")
    data = {"email": user.email, "password": "password123"}

    response = client.post(url, data)

    assert response.status_code == 200
    assert response.data["detail"] == "Login successful"

    # Check that JWT cookies are set
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

    # Verify cookies have correct properties
    access_cookie = response.cookies["access_token"]
    refresh_cookie = response.cookies["refresh_token"]

    assert access_cookie["httponly"] is True
    assert access_cookie["secure"] is True
    assert access_cookie["samesite"] == "None"

    assert refresh_cookie["httponly"] is True
    assert refresh_cookie["secure"] is True
    assert refresh_cookie["samesite"] == "None"

@pytest.mark.django_db
def test_login_fail(client):
    user = User.objects.create_user(email="loginfail@example.com", password="password123", is_active=True)

    url = reverse("token_obtain_pair")
    data = {"email": user.email, "password": "wrongpassword"}

    response = client.post(url, data)

    assert response.status_code == 401
    assert "detail" in response.data
    assert "No active account found" in str(response.data["detail"]) or "Invalid credentials" in str(response.data["detail"])
    assert "detail" in response.data
    assert "No active account found" in str(response.data["detail"]) or "Invalid credentials" in str(response.data["detail"])
