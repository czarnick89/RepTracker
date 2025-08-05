import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from workouts.models import Workout
from users.models import User
from datetime import date, timedelta

@pytest.mark.django_db
class TestWorkoutViewSet:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@example.com', password='password123')
        self.client.force_authenticate(user=self.user)

        # Create some workouts owned by this user
        self.workout1 = Workout.objects.create(
            user=self.user,
            workout_number=1,
            name="Workout 1",
            date=date.today()
        )
        self.workout2 = Workout.objects.create(
            user=self.user,
            workout_number=2,
            name="Workout 2",
            date=date.today() - timedelta(days=1)
        )

        # Create workout for another user to test isolation
        self.other_user = User.objects.create_user(email='otheruser@example.com', password='password456')
        self.other_workout = Workout.objects.create(
            user=self.other_user,
            workout_number=1,
            name="Other User Workout",
            date=date.today()
        )

    def test_list_workouts_only_returns_user_workouts(self):
        url = reverse('workout-list')
        response = self.client.get(url)
        assert response.status_code == 200
        # Should only include this user's workouts
        returned_ids = {w['id'] for w in response.data}
        assert self.workout1.id in returned_ids
        assert self.workout2.id in returned_ids
        assert self.other_workout.id not in returned_ids

    def test_create_workout_auto_assigns_user_and_workout_number(self):
        url = reverse('workout-list')
        data = {
            "name": "New Workout",
            "date": str(date.today() + timedelta(days=1)),
            "notes": "Test notes"
            # no workout_number included, should auto assign
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == 201
        assert response.data['user'] == self.user.id
        # workout_number should be last + 1 (which was 2)
        assert response.data['workout_number'] == 3
        assert response.data['name'] == "New Workout"

    def test_retrieve_workout(self):
        url = reverse('workout-detail', args=[self.workout1.id])
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data['id'] == self.workout1.id
        assert response.data['name'] == self.workout1.name

    def test_update_workout(self):
        url = reverse('workout-detail', args=[self.workout1.id])
        update_data = {"name": "Updated Workout Name"}
        response = self.client.patch(url, update_data, format='json')
        assert response.status_code == 200
        assert response.data['name'] == "Updated Workout Name"

    def test_delete_workout(self):
        url = reverse('workout-detail', args=[self.workout2.id])
        response = self.client.delete(url)
        assert response.status_code == 204
        assert not Workout.objects.filter(id=self.workout2.id).exists()

    def test_cannot_access_other_user_workouts(self):
        url = reverse('workout-detail', args=[self.other_workout.id])
        response = self.client.get(url)
        # Should be 404 because get_queryset filters by user
        assert response.status_code == 404

    def test_unauthenticated_access_denied(self):
        self.client.force_authenticate(user=None)
        url = reverse('workout-list')
        response = self.client.get(url)
        assert response.status_code == 401  # Unauthorized
