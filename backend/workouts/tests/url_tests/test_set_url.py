import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from workouts.models import Set, Exercise, Workout
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

@pytest.mark.django_db
class TestSetURLs:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='user@example.com', password='testpass')
        self.client.force_authenticate(user=self.user)

        # Create a workout, exercise, and a set
        self.workout = Workout.objects.create(user=self.user, name='Workout 1', workout_number=1, date=date.today())
        self.exercise = Exercise.objects.create(workout=self.workout, name='Exercise 1', exercise_number=1)
        self.set = Set.objects.create(exercise=self.exercise, set_number=1, reps=10, weight=100)

        self.list_url = reverse('set-list')  # from router: 'sets'
        self.detail_url = reverse('set-detail', args=[self.set.id])

    def test_list_sets(self):
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert any(s['id'] == self.set.id for s in response.data)

    def test_retrieve_set(self):
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == self.set.id

    def test_create_set(self):
        data = {
            "exercise": self.exercise.id,
            "reps": 8,
            "weight": 120
        }
        response = self.client.post(self.list_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['exercise'] == self.exercise.id
        assert response.data['reps'] == 8

    def test_update_set(self):
        data = {
            "reps": 12,
            "weight": 130
        }
        response = self.client.patch(self.detail_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['reps'] == 12
        assert response.data['weight'] == '130.00'  # decimal serialized as string

    def test_delete_set(self):
        response = self.client.delete(self.detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Set.objects.filter(id=self.set.id).exists()

    def test_unauthenticated_access_denied(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
