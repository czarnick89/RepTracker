import pytest
from rest_framework.test import APIClient
from workouts.models import Set, Exercise, Workout
from users.models import User
from django.urls import reverse
from datetime import date

@pytest.mark.django_db
class TestSetViewSet:
    def setup_method(self):
        self.user = User.objects.create_user(email="testuser@example.com", password="password123")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create workout and exercise for FK relations
        self.workout = Workout.objects.create(user=self.user, workout_number=1, name="Workout 1", date=date.today())
        self.exercise = Exercise.objects.create(workout=self.workout, name="Squat", exercise_number=1)

        # Create an initial set
        self.set = Set.objects.create(exercise=self.exercise, set_number=1, reps=8, weight=135)

    def test_list_sets(self):
        url = reverse('set-list')  # Depends on your router naming
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.data) >= 1  # At least the one created

    def test_retrieve_set(self):
        url = reverse('set-detail', args=[self.set.id])
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data['id'] == self.set.id

    def test_create_set(self):
        url = reverse('set-list')
        data = {
            "exercise": self.exercise.id,
            "reps": 10,
            "weight": 140
            # no set_number, test auto-assignment in serializer
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == 201
        assert response.data['set_number'] == 2  # auto incremented

    def test_update_set(self):
        url = reverse('set-detail', args=[self.set.id])
        data = {
            "reps": 12,
            "weight": 150
        }
        response = self.client.patch(url, data, format='json')
        assert response.status_code == 200
        assert response.data['reps'] == 12
        assert float(response.data['weight']) == 150

    def test_delete_set(self):
        url = reverse('set-detail', args=[self.set.id])
        response = self.client.delete(url)
        assert response.status_code == 204
        assert Set.objects.filter(id=self.set.id).count() == 0

    def test_unauthenticated_access_denied(self):
        self.client.force_authenticate(user=None)
        url = reverse('set-list')
        response = self.client.get(url)
        assert response.status_code == 401
