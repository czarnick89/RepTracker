import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from workouts.models import TemplateSet, TemplateExercise, TemplateWorkout
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestTemplateSetURLs:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='user@example.com', password='password123')
        self.client.force_authenticate(user=self.user)

        self.template_workout = TemplateWorkout.objects.create(
            user=self.user,
            template_number=1,
            name="Template Workout 1",
            description="Sample description"
        )

        self.template_exercise = TemplateExercise.objects.create(
            workout_template=self.template_workout,
            name="Exercise 1",
            exercise_number=1
        )

        self.template_set = TemplateSet.objects.create(
            exercise=self.template_exercise,
            set_number=1
        )

        self.list_url = reverse('templateset-list')
        self.detail_url = reverse('templateset-detail', args=[self.template_set.id])

    def test_list_template_sets(self):
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        # Only sets belonging to user's templates
        assert any(s['id'] == self.template_set.id for s in response.data)

    def test_retrieve_template_set(self):
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == self.template_set.id
        assert response.data['exercise'] == self.template_exercise.id

    def test_create_template_set(self):
        data = {
            "exercise": self.template_exercise.id,
            "set_number": 2
        }
        response = self.client.post(self.list_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['set_number'] == 2

    def test_update_template_set(self):
        data = {
            "set_number": 10
        }
        response = self.client.patch(self.detail_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['set_number'] == 10

    def test_delete_template_set(self):
        response = self.client.delete(self.detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not TemplateSet.objects.filter(id=self.template_set.id).exists()

    def test_unauthenticated_access_denied(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_create_set_for_other_user_template(self):
        other_user = User.objects.create_user(email='other@example.com', password='password123')
        other_template_workout = TemplateWorkout.objects.create(
            user=other_user,
            template_number=1,
            name="Other Template"
        )
        other_exercise = TemplateExercise.objects.create(
            workout_template=other_template_workout,
            name="Other Exercise",
            exercise_number=1
        )

        data = {
            "exercise": other_exercise.id,
            "set_number": 1
        }
        response = self.client.post(self.list_url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
