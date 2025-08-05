import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from workouts.models import TemplateExercise, TemplateWorkout
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestTemplateExerciseURLs:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='user@example.com', password='password123')
        self.client.force_authenticate(user=self.user)

        self.template_workout = TemplateWorkout.objects.create(
            user=self.user,
            template_number=1,
            name="Workout Template 1",
            description="Desc"
        )

        self.template_exercise = TemplateExercise.objects.create(
            workout_template=self.template_workout,
            name="Exercise 1",
            exercise_number=1
        )

        self.list_url = reverse('templateexercise-list')
        self.detail_url = reverse('templateexercise-detail', args=[self.template_exercise.id])

    def test_list_template_exercises(self):
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        # Only exercises for user's templates
        assert any(e['id'] == self.template_exercise.id for e in response.data)

    def test_retrieve_template_exercise(self):
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == self.template_exercise.id
        assert response.data['workout_template'] == self.template_workout.id

    def test_create_template_exercise(self):
        data = {
            "workout_template": self.template_workout.id,
            "name": "Exercise 2",
            "exercise_number": 2
        }
        response = self.client.post(self.list_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == "Exercise 2"

    def test_create_template_exercise_without_exercise_number_auto_increment(self):
        template = TemplateWorkout.objects.create(
            user=self.user,
            template_number=99,
            name="Fresh Template"
        )

        TemplateExercise.objects.create(
            workout_template=template,
            name="Existing Exercise",
            exercise_number=1
        )

        data = {
            "workout_template": template.id,
            "name": "New Exercise"  # no number
        }

        response = self.client.post(self.list_url, data)
        assert response.status_code == 201
        assert response.data['exercise_number'] == 2

    def test_update_template_exercise(self):
        data = {
            "name": "Updated Exercise"
        }
        response = self.client.patch(self.detail_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == "Updated Exercise"

    def test_update_cannot_change_workout_template(self):
        other_workout = TemplateWorkout.objects.create(
            user=self.user,
            template_number=2,
            name="Other Template"
        )
        data = {
            "workout_template": other_workout.id,  # should be ignored
            "name": "Try to change workout_template"
        }
        response = self.client.patch(self.detail_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['workout_template'] == self.template_workout.id  # Not changed

    def test_delete_template_exercise(self):
        response = self.client.delete(self.detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not TemplateExercise.objects.filter(id=self.template_exercise.id).exists()

    def test_create_for_other_users_template_denied(self):
        other_user = User.objects.create_user(email='other@example.com', password='password123')
        other_template = TemplateWorkout.objects.create(
            user=other_user,
            template_number=1,
            name="Other User Template"
        )
        data = {
            "workout_template": other_template.id,
            "name": "Unauthorized Exercise",
            "exercise_number": 1
        }
        response = self.client.post(self.list_url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_access_denied(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
