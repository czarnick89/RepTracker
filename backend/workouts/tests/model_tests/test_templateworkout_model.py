import pytest
from django.db import IntegrityError
from workouts.models import TemplateWorkout
from django.contrib.auth import get_user_model

@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(email="user@example.com", password="pass1234")

@pytest.mark.django_db
class TestTemplateWorkoutModel:

    def test_create_template_workout(self, user):
        tw = TemplateWorkout.objects.create(
            user=user,
            template_number=1,
            name="Full Body Template",
            description="A great all-round workout template"
        )
        assert tw.user == user
        assert tw.template_number == 1
        assert tw.name == "Full Body Template"
        assert tw.description == "A great all-round workout template"
        assert tw.created_at is not None
        assert tw.updated_at is not None

    def test_str_method(self, user):
        tw = TemplateWorkout.objects.create(user=user, template_number=2, name="Leg Day")
        expected = f"Template 'Leg Day' by {user.email}"
        assert str(tw) == expected

    def test_ordering_by_template_number(self, user):
        tw1 = TemplateWorkout.objects.create(user=user, template_number=2, name="Template B")
        tw2 = TemplateWorkout.objects.create(user=user, template_number=1, name="Template A")
        workouts = list(TemplateWorkout.objects.filter(user=user))
        assert workouts[0] == tw2
        assert workouts[1] == tw1

    def test_unique_template_number_constraint(self, user):
        TemplateWorkout.objects.create(user=user, template_number=1, name="Template One")
        with pytest.raises(IntegrityError):
            TemplateWorkout.objects.create(user=user, template_number=1, name="Duplicate Template")
