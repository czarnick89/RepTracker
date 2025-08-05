import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from workouts.models import TemplateWorkout, TemplateExercise
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

User = get_user_model()

@pytest.mark.django_db
class TestTemplateExerciseViewSet:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user = User.objects.create_user(email="user@example.com", password="pass1234")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        # Create a TemplateWorkout owned by user
        self.template_workout = TemplateWorkout.objects.create(
            user=self.user,
            template_number=1,
            name="Template Workout 1",
            description="Desc"
        )

        # Create a TemplateExercise under that workout
        self.template_exercise = TemplateExercise.objects.create(
            workout_template=self.template_workout,
            name="Exercise 1",
            exercise_number=1
        )

        self.list_url = reverse('templateexercise-list')

    def test_list_template_exercises(self):
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        results = response.json()
        assert any(ex['id'] == self.template_exercise.id for ex in results)

    def test_create_template_exercise_valid(self):
        data = {
            "workout_template": self.template_workout.id,
            "name": "Exercise 2",
            "exercise_number": 2
        }
        response = self.client.post(self.list_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['name'] == "Exercise 2"

    def test_create_template_exercise_forbidden(self):
        other_user = User.objects.create_user(email="other@example.com", password="pass1234")
        other_workout = TemplateWorkout.objects.create(
            user=other_user,
            template_number=1,
            name="Other Workout",
            description="Desc"
        )
        data = {
            "workout_template": other_workout.id,
            "name": "Bad Exercise",
            "exercise_number": 1
        }
        response = self.client.post(self.list_url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_template_exercise(self):
        url = reverse('templateexercise-detail', args=[self.template_exercise.id])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['id'] == self.template_exercise.id

    def test_update_template_exercise(self):
        url = reverse('templateexercise-detail', args=[self.template_exercise.id])
        data = {
            "name": "Updated Exercise",
            "workout_template": self.template_workout.id  # should be ignored by perform_update
        }
        response = self.client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['name'] == "Updated Exercise"

    def test_update_template_exercise_prevents_changing_workout_template(self):
        url = reverse('templateexercise-detail', args=[self.template_exercise.id])
        other_workout = TemplateWorkout.objects.create(
            user=self.user,
            template_number=2,
            name="Other Template Workout"
        )
        data = {
            "workout_template": other_workout.id
        }
        response = self.client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        # Confirm workout_template was NOT changed
        obj = TemplateExercise.objects.get(id=self.template_exercise.id)
        assert obj.workout_template.id == self.template_workout.id

    def test_delete_template_exercise(self):
        url = reverse('templateexercise-detail', args=[self.template_exercise.id])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not TemplateExercise.objects.filter(id=self.template_exercise.id).exists()

    def test_delete_template_exercise_forbidden(self):
        # Create exercise owned by other user
        other_user = User.objects.create_user(email="other@example.com", password="pass1234")
        other_workout = TemplateWorkout.objects.create(
            user=other_user,
            template_number=1,
            name="Other Workout"
        )
        other_exercise = TemplateExercise.objects.create(
            workout_template=other_workout,
            name="Other Exercise",
            exercise_number=1
        )
        url = reverse('templateexercise-detail', args=[other_exercise.id])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_access_denied(self):
        client = APIClient()
        response = client.get(self.list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
