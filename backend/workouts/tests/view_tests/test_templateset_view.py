import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from workouts.models import TemplateSet, TemplateExercise, TemplateWorkout
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

@pytest.mark.django_db
class TestTemplateSetViewSet:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Create user and login client
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

        # Create a TemplateSet under that exercise
        self.template_set = TemplateSet.objects.create(
            exercise=self.template_exercise,
            set_number=1
        )

        self.list_url = reverse('templateset-list')

    def test_list_template_sets(self):
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        # Should only return sets for this user
        results = response.json()
        assert any(ts['id'] == self.template_set.id for ts in results)

    def test_create_template_set_valid(self):
        data = {
            "exercise": self.template_exercise.id,
            "set_number": 2
        }
        response = self.client.post(self.list_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['set_number'] == 2

    def test_create_template_set_invalid_exercise(self):
        # Create another user and exercise owned by them
        other_user = User.objects.create_user(email="other@example.com", password="pass1234")
        other_workout = TemplateWorkout.objects.create(
            user=other_user,
            template_number=1,
            name="Other Workout",
            description="Desc"
        )
        other_exercise = TemplateExercise.objects.create(
            workout_template=other_workout,
            name="Other Exercise",
            exercise_number=1
        )

        data = {
            "exercise": other_exercise.id,
            "set_number": 1
        }
        response = self.client.post(self.list_url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_template_set(self):
        url = reverse('templateset-detail', args=[self.template_set.id])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['id'] == self.template_set.id

    def test_update_template_set(self):
        url = reverse('templateset-detail', args=[self.template_set.id])
        data = {"set_number": 10}
        response = self.client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['set_number'] == 10

    def test_delete_template_set(self):
        url = reverse('templateset-detail', args=[self.template_set.id])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not TemplateSet.objects.filter(id=self.template_set.id).exists()

    def test_unauthenticated_access_denied(self):
        client = APIClient()  # no auth
        response = client.get(self.list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
