import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
def test_logout_without_token():
    client = APIClient()
    url = reverse('logout')
    response = client.post(url)
    assert response.status_code == status.HTTP_200_OK
    assert "logged out" in response.data["detail"].lower()
