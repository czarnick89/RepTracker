import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from workouts.models import TemplateWorkout
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(email="user@example.com", password="password123")

@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def template_workout(user):
    return TemplateWorkout.objects.create(
        user=user,
        template_number=1,
        name="Test Template Workout",
        description="A test template workout"
    )

@pytest.mark.django_db
class TestTemplateWorkoutURLs:
    @pytest.fixture(autouse=True)
    def setup_urls(self, template_workout):
        self.list_url = reverse('templateworkout-list')
        self.detail_url = reverse('templateworkout-detail', args=[template_workout.id])

    def test_create_template_workout_without_template_number_auto_increments(self, api_client, user):
        data = {
            "name": "New Template Workout",
            "description": "Testing auto increment",
            # no template_number provided
        }
        response = api_client.post(self.list_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["template_number"] == 2  # Should auto increment from existing max

    def test_create_template_workout_with_specific_template_number(self, api_client):
        data = {
            "name": "Specific Number Workout",
            "description": "Explicit number",
            "template_number": 10
        }
        response = api_client.post(self.list_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["template_number"] == 10

    def test_create_duplicate_template_number_for_same_user_fails(self, api_client, template_workout):
        data = {
            "name": "Duplicate Number",
            "description": "This should fail",
            "template_number": template_workout.template_number  # 1
        }
        response = api_client.post(self.list_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'template_number' in response.data

    def test_list_returns_only_user_template_workouts(self, api_client, user):
        # Create a workout for a different user
        other_user = User.objects.create_user(email="other@example.com", password="password123")
        TemplateWorkout.objects.create(
            user=other_user,
            template_number=1,
            name="Other User Workout",
            description="Not yours"
        )
        response = api_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        # All returned workouts must belong to logged-in user
        assert all(tw['user'] == user.id for tw in response.data)

    def test_update_template_workout(self, api_client, template_workout):
        data = {
            "name": "Updated Name",
            "description": "Updated description"
        }
        response = api_client.patch(self.detail_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == "Updated Name"
        assert response.data['description'] == "Updated description"

    def test_user_cannot_change_user_field_on_update(self, api_client, template_workout):
        # Attempt to change the owner user field (should be ignored)
        other_user = User.objects.create_user(email="other2@example.com", password="password123")
        data = {
            "user": other_user.id
        }
        response = api_client.patch(self.detail_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user'] == template_workout.user.id  # user unchanged

    def test_delete_template_workout(self, api_client, template_workout):
        response = api_client.delete(self.detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not TemplateWorkout.objects.filter(id=template_workout.id).exists()

    def test_delete_other_users_template_workout_forbidden(self, api_client, user):
        # Create workout owned by other user
        other_user = User.objects.create_user(email="other3@example.com", password="password123")
        other_template = TemplateWorkout.objects.create(
            user=other_user,
            template_number=1,
            name="Other's Template",
            description="Should not delete"
        )
        url = reverse('templateworkout-detail', args=[other_template.id])
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_access_denied(self):
        client = APIClient()  # no authentication
        response = client.get(self.list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
