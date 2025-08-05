import pytest
from workouts.models import Exercise, Workout
from django.db import IntegrityError
from datetime import date

@pytest.fixture
def workout(django_user_model):
    user = django_user_model.objects.create_user(email="test@example.com", password="pass1234")
    return Workout.objects.create(user=user, workout_number=1, name="Leg Day", date=date.today())

@pytest.mark.django_db
class TestExerciseModel:

    def test_create_exercise(self, workout):
        exercise = Exercise.objects.create(workout=workout, name="Squat", exercise_number=1)
        assert exercise.name == "Squat"
        assert exercise.exercise_number == 1
        assert exercise.workout == workout

    def test_str_method(self, workout):
        exercise = Exercise.objects.create(workout=workout, name="Bench Press", exercise_number=2)
        expected = f"Exercise 2: Bench Press (Workout ID: {workout.id})"
        assert str(exercise) == expected

    def test_ordering_by_exercise_number(self, workout):
        ex1 = Exercise.objects.create(workout=workout, name="A", exercise_number=2)
        ex2 = Exercise.objects.create(workout=workout, name="B", exercise_number=1)
        exercises = list(Exercise.objects.filter(workout=workout))
        assert exercises[0] == ex2
        assert exercises[1] == ex1

    def test_unique_exercise_number_constraint(self, workout):
        Exercise.objects.create(workout=workout, name="Squat", exercise_number=1)
        with pytest.raises(IntegrityError):
            Exercise.objects.create(workout=workout, name="Deadlift", exercise_number=1)
