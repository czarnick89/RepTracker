import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from workouts.models import Exercise, Workout
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

@pytest.mark.django_db
class TestExerciseURLs:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='user@example.com', password='testpass')
        self.client.force_authenticate(user=self.user)

        self.workout = Workout.objects.create(user=self.user, name='Workout 1', workout_number=1, date=date.today())
        self.exercise = Exercise.objects.create(workout=self.workout, name='Exercise 1', exercise_number=1)

        self.list_url = reverse('exercise-list')  # from router: 'exercises'
        self.detail_url = reverse('exercise-detail', args=[self.exercise.id])

    def test_list_exercises(self):
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert any(e['id'] == self.exercise.id for e in response.data)

    def test_retrieve_exercise(self):
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == self.exercise.id

    def test_create_exercise(self):
        data = {
            "workout": self.workout.id,
            "name": "New Exercise",
            # omit exercise_number to test auto increment logic
        }
        response = self.client.post(self.list_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == "New Exercise"
        assert response.data['workout'] == self.workout.id
        assert response.data['exercise_number'] == 2  # auto incremented

    def test_update_exercise(self):
        data = {
            "name": "Updated Exercise",
            "exercise_number": 1  # should be allowed to update
        }
        response = self.client.patch(self.detail_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == "Updated Exercise"

    def test_delete_exercise(self):
        response = self.client.delete(self.detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Exercise.objects.filter(id=self.exercise.id).exists()

    def test_unauthenticated_access_denied(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
