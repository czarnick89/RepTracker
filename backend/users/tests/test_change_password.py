import pytest
from rest_framework import status
from django.urls import reverse

@pytest.mark.django_db
class TestChangePasswordView:

    @pytest.fixture(autouse=True)
    def setup(self, authenticated_client, verified_user):
        self.client = authenticated_client
        self.user = verified_user
        self.url = reverse('change-password')

    def test_change_password_success(self):
        data = {
            "old_password": "strongpassword123",
            "new_password": "NewStrongPass123"
        }
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "Password changed successfully" in response.data["detail"]

        self.user.refresh_from_db()
        assert self.user.check_password("NewStrongPass123")

    def test_wrong_old_password(self):
        data = {
            "old_password": "wrongpassword",
            "new_password": "NewStrongPass123"
        }
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Old password is incorrect" in response.data["error"]

    def test_weak_new_password(self):
        data = {
            "old_password": "strongpassword123",
            "new_password": "123"
        }
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert isinstance(response.data["error"], list)  # Validation errors come as list of strings

    def test_missing_old_password(self):
        data = {
            "new_password": "NewStrongPass123"
        }
        response = self.client.post(self.url, data)
        # The view does not explicitly check this, so likely it will treat None as wrong password:
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Old password is incorrect" in response.data["error"]

    def test_missing_new_password(self):
        data = {
            "old_password": "strongpassword123"
        }
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "New password is required." in response.data["error"]
