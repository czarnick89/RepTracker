import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from workouts.models import Exercise, Workout
from users.models import User  

@pytest.mark.django_db
class TestExerciseViewSet:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@example.com', password='password123')
        self.client.force_authenticate(user=self.user)

        self.workout = Workout.objects.create(
            user=self.user,
            workout_number=1,
            name="Test Workout",
            date="2025-08-05"
        )

    def test_list_exercises_empty(self):
        url = reverse('exercise-list')
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data == []

    def test_create_exercise(self):
        url = reverse('exercise-list')
        data = {
            "workout": self.workout.id,
            "name": "Squat",
            "exercise_number": 1,
            "weight_change_preference": "same",  # if applicable
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == 201
        assert response.data['name'] == "Squat"
        assert response.data['exercise_number'] == 1
        assert response.data['workout'] == self.workout.id

    def test_retrieve_exercise(self):
        exercise = Exercise.objects.create(
            workout=self.workout,
            name="Bench Press",
            exercise_number=2,
            weight_change_preference="increase"
        )
        url = reverse('exercise-detail', args=[exercise.id])
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data['name'] == exercise.name

    def test_update_exercise(self):
        exercise = Exercise.objects.create(
            workout=self.workout,
            name="Bench Press",
            exercise_number=2,
            weight_change_preference="increase"
        )
        url = reverse('exercise-detail', args=[exercise.id])
        update_data = {"name": "Incline Bench Press"}
        response = self.client.patch(url, update_data, format='json')
        assert response.status_code == 200
        assert response.data['name'] == "Incline Bench Press"

    def test_delete_exercise(self):
        exercise = Exercise.objects.create(
            workout=self.workout,
            name="Deadlift",
            exercise_number=3,
            weight_change_preference="decrease"
        )
        url = reverse('exercise-detail', args=[exercise.id])
        response = self.client.delete(url)
        assert response.status_code == 204
        assert not Exercise.objects.filter(id=exercise.id).exists()

    def test_unauthenticated_access_denied(self):
        self.client.force_authenticate(user=None)
        url = reverse('exercise-list')
        response = self.client.get(url)
        assert response.status_code == 401  # Unauthorized
