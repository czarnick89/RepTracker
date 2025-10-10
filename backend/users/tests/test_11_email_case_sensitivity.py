import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
def test_login_email_case_insensitivity(create_user, api_client):
    # Create a user with lowercase email
    user_email = "testuser@example.com"
    user_password = "StrongPass123"
    create_user(email=user_email, password=user_password)

    login_url = reverse("token_obtain_pair")

    # Try logging in with uppercase email
    login_data = {
        "email": user_email.upper(),
        "password": user_password,
    }
    response = api_client.post(login_url, login_data)
    
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies
