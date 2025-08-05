import pytest
from django.db import IntegrityError
from workouts.models import TemplateExercise, TemplateWorkout
from django.contrib.auth import get_user_model


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(email="user@example.com", password="pass1234")

@pytest.mark.django_db
class TestTemplateExerciseModel:

    @pytest.fixture
    def template_workout(self, user):
        return TemplateWorkout.objects.create(user=user, template_number=1, name="Template 1")

    def test_create_template_exercise(self, template_workout):
        te = TemplateExercise.objects.create(workout_template=template_workout, name="Pushup", exercise_number=1)
        assert te.workout_template == template_workout
        assert te.name == "Pushup"
        assert te.exercise_number == 1
        assert te.created_at is not None
        assert te.updated_at is not None

    def test_str_method(self, template_workout):
        te = TemplateExercise.objects.create(workout_template=template_workout, name="Squat", exercise_number=2)
        expected = f"Template Exercise 2: Squat"
        assert str(te) == expected

    def test_ordering_by_exercise_number(self, template_workout):
        te1 = TemplateExercise.objects.create(workout_template=template_workout, name="B", exercise_number=2)
        te2 = TemplateExercise.objects.create(workout_template=template_workout, name="A", exercise_number=1)
        exercises = list(TemplateExercise.objects.filter(workout_template=template_workout))
        assert exercises[0] == te2
        assert exercises[1] == te1

    def test_unique_constraint(self, template_workout):
        TemplateExercise.objects.create(workout_template=template_workout, name="Bench Press", exercise_number=1)
        with pytest.raises(IntegrityError):
            TemplateExercise.objects.create(workout_template=template_workout, name="Deadlift", exercise_number=1)
