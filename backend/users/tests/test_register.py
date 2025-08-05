import pytest
from django.core import mail
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

@pytest.mark.django_db
def test_user_register(api_client):
    data = {
        "email": "newuser@example.com",
        "password": "strongpassword123"
    }

    response = api_client.post(reverse('register'), data)

    assert response.status_code == 201
    assert response.data["detail"] == "Check your email to verify your account."

    # Ensure user exists in DB, but is inactive
    user = User.objects.get(email="newuser@example.com")
    assert not user.is_active

    # Ensure verification email was sent
    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert "Verify your email" in email.subject
    assert "http://" in email.body  # contains verification link
    assert user.email in email.to
