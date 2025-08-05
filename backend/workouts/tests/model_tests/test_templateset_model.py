import pytest
from django.db import IntegrityError
from workouts.models import TemplateSet, TemplateExercise, TemplateWorkout
from django.contrib.auth import get_user_model
from datetime import date

@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(email="user@example.com", password="pass1234")

@pytest.mark.django_db
class TestTemplateSetModel:

    @pytest.fixture
    def template_workout(self, user):
        return TemplateWorkout.objects.create(user=user, template_number=1, name="Template 1")

    @pytest.fixture
    def template_exercise(self, template_workout):
        return TemplateExercise.objects.create(workout_template=template_workout, name="Pushup", exercise_number=1)

    def test_create_template_set(self, template_exercise):
        ts = TemplateSet.objects.create(exercise=template_exercise, set_number=1)
        assert ts.exercise == template_exercise
        assert ts.set_number == 1
        assert ts.created_at is not None
        assert ts.updated_at is not None

    def test_str_method(self, template_exercise):
        ts = TemplateSet.objects.create(exercise=template_exercise, set_number=2)
        expected = f"Template Set 2 for Exercise {template_exercise.id}"
        assert str(ts) == expected

    def test_ordering_by_set_number(self, template_exercise):
        ts1 = TemplateSet.objects.create(exercise=template_exercise, set_number=2)
        ts2 = TemplateSet.objects.create(exercise=template_exercise, set_number=1)
        sets = list(TemplateSet.objects.filter(exercise=template_exercise))
        assert sets[0] == ts2
        assert sets[1] == ts1

    def test_unique_constraint(self, template_exercise):
        TemplateSet.objects.create(exercise=template_exercise, set_number=1)
        with pytest.raises(IntegrityError):
            TemplateSet.objects.create(exercise=template_exercise, set_number=1)
