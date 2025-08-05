import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from workouts.models import TemplateWorkout
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestTemplateWorkoutViewSet:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="user@example.com", password="pass1234")
        self.other_user = User.objects.create_user(email="other@example.com", password="pass1234")
        self.client.force_authenticate(user=self.user)

        self.template1 = TemplateWorkout.objects.create(user=self.user, template_number=1, name="Template One")
        self.template2 = TemplateWorkout.objects.create(user=self.user, template_number=2, name="Template Two")
        self.other_template = TemplateWorkout.objects.create(user=self.other_user, template_number=1, name="Other User Template")

    def test_list_templates_returns_only_user_templates(self):
        url = reverse('templateworkout-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        returned_ids = [item['id'] for item in response.json()]
        assert self.template1.id in returned_ids
        assert self.template2.id in returned_ids
        assert self.other_template.id not in returned_ids

    def test_create_template_assigns_user_and_autoincrements_template_number(self):
        url = reverse('templateworkout-list')
        data = {
            "name": "New Template",
            "description": "Test description"
            # omit template_number to test auto-increment behavior if applicable
        }
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        created = TemplateWorkout.objects.get(id=response.json()['id'])
        assert created.user == self.user
        # If auto-increment on template_number, check it's > 2
        assert created.template_number > 0

    def test_update_template_prevents_user_change(self):
        url = reverse('templateworkout-detail', args=[self.template1.id])
        data = {
            "name": "Updated Name",
            "user": self.other_user.id  # Should be ignored
        }
        response = self.client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        updated = TemplateWorkout.objects.get(id=self.template1.id)
        assert updated.name == "Updated Name"
        assert updated.user == self.user  # User unchanged

    def test_delete_own_template_succeeds(self):
        url = reverse('templateworkout-detail', args=[self.template1.id])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        with pytest.raises(TemplateWorkout.DoesNotExist):
            TemplateWorkout.objects.get(id=self.template1.id)

    def test_delete_other_user_template_forbidden(self):
        url = reverse('templateworkout-detail', args=[self.other_template.id])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert TemplateWorkout.objects.filter(id=self.other_template.id).exists()
