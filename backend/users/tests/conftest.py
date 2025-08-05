import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def make_user(**kwargs):
        defaults = {
            "email": "user@example.com",
            "password": "strongpassword123",
            "is_active": True,
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
    return make_user

@pytest.fixture
def inactive_user(create_user):
    return create_user(is_active=False)

@pytest.fixture
def verified_user(create_user):
    return create_user(is_active=True)

@pytest.fixture
def authenticated_client(verified_user):
    client = APIClient()
    client.force_authenticate(user=verified_user)
    return client
