import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from workouts.models import Workout
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

@pytest.mark.django_db
class TestWorkoutURLs:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='user@example.com', password='testpass')
        self.client.force_authenticate(user=self.user)

        self.workout = Workout.objects.create(
            user=self.user,
            name='Workout 1',
            workout_number=1,
            date=date.today()
        )

        self.list_url = reverse('workout-list')  # from router: 'workouts'
        self.detail_url = reverse('workout-detail', args=[self.workout.id])

    def test_list_workouts(self):
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        # Should only list workouts belonging to user
        assert any(w['id'] == self.workout.id for w in response.data)

    def test_retrieve_workout(self):
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == self.workout.id
        assert response.data['user'] == self.user.id

    def test_create_workout(self):
        data = {
            "name": "New Workout",
            "date": str(date.today()),  # date string in ISO format
            # omit workout_number to test auto increment
        }
        response = self.client.post(self.list_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == "New Workout"
        assert response.data['user'] == self.user.id
        assert response.data['workout_number'] == 2  # auto incremented

    def test_update_workout(self):
        data = {
            "name": "Updated Workout",
            "workout_number": 1
        }
        response = self.client.patch(self.detail_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == "Updated Workout"

    def test_delete_workout(self):
        response = self.client.delete(self.detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Workout.objects.filter(id=self.workout.id).exists()

    def test_unauthenticated_access_denied(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
