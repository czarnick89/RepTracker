import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_register_cannot_set_privileged_fields(client):
    url = reverse('register')

    payload = {
        "email": "attacker@example.com",
        "password": "strongpassword123",
        "is_staff": True,
        "is_superuser": True,
        "is_active": True  # also try to sneak in active status
    }

    response = client.post(url, payload)

    assert response.status_code == 201

    # Get the created user from DB
    user = User.objects.get(email="attacker@example.com")

    # Privileged fields should be False (default)
    assert user.is_staff is False
    assert user.is_superuser is False
    # Also check is_active is False (since your create_user sets inactive on registration)
    assert user.is_active is False
