import pytest
from rest_framework import status
from django.urls import reverse

@pytest.mark.django_db
class TestUserProfileView:

    @pytest.fixture(autouse=True)
    def setup(self, api_client, verified_user):
        self.client = api_client
        self.user = verified_user
        self.url = reverse("user-profile")
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == self.user.email
        assert "id" in response.data

    def test_put_profile_success(self):
        # Assuming your UserProfileSerializer allows updating fields
        # Here we try updating a field (add one if needed, like 'first_name')
        data = {
            # example field to update, adjust as your model/serializer supports
            # "first_name": "UpdatedName"
        }
        # If no updatable fields yet, this test will be minimal:
        response = self.client.put(self.url, data)
        assert response.status_code == status.HTTP_200_OK
        # Confirm the data returned matches what was sent or unchanged if no fields

    def test_put_profile_invalid(self):
        data = {
            "first_name": ""  # empty string should fail if allow_blank=False
        }
        response = self.client.put(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
