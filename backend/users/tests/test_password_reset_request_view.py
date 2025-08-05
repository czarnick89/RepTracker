import pytest
from django.urls import reverse
from django.core import mail


@pytest.mark.django_db
class TestPasswordResetRequestView:

    def test_valid_reset_request(self, api_client, verified_user):
        url = reverse("password-reset-request")
        response = api_client.post(url, {"email": verified_user.email})

        assert response.status_code == 200
        assert "reset link has been sent" in response.data["detail"].lower()
        assert len(mail.outbox) == 1
        assert verified_user.email in mail.outbox[0].to

    def test_reset_request_for_inactive_user(self, api_client, inactive_user):
        url = reverse("password-reset-request")
        response = api_client.post(url, {"email": inactive_user.email})

        assert response.status_code == 400
        assert "inactive account" in response.data["error"].lower()
        assert len(mail.outbox) == 0

    def test_reset_request_with_blank_email(self, api_client):
        url = reverse("password-reset-request")
        response = api_client.post(url, {"email": ""})

        assert response.status_code == 400
        assert "email is required" in response.data["error"].lower()

    def test_reset_request_for_nonexistent_user(self, api_client):
        url = reverse("password-reset-request")
        response = api_client.post(url, {"email": "nonexistent@example.com"})

        assert response.status_code == 200
        assert "reset link has been sent" in response.data["detail"].lower()
        assert len(mail.outbox) == 0
