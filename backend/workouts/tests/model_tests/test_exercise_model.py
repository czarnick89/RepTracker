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

    def test_weight_change_preference_default(self, workout):
        """Test that weight_change_preference defaults to 'same'."""
        exercise = Exercise.objects.create(workout=workout, name="Bench Press", exercise_number=1)
        assert exercise.weight_change_preference == 'same'

    def test_weight_change_preference_choices(self, workout):
        """Test valid weight_change_preference choices."""
        # Test all valid choices
        for choice in ['increase', 'decrease', 'same']:
            exercise = Exercise.objects.create(
                workout=workout, 
                name=f"Exercise {choice}", 
                exercise_number=10 + ['increase', 'decrease', 'same'].index(choice),
                weight_change_preference=choice
            )
            assert exercise.weight_change_preference == choice

    def test_exercise_number_can_be_null(self, workout):
        """Test that exercise_number can be null."""
        exercise = Exercise.objects.create(workout=workout, name="Test Exercise")
        assert exercise.exercise_number is None
        assert exercise.name == "Test Exercise"

    def test_exercise_number_can_be_blank(self, workout):
        """Test that exercise_number can be blank."""
        exercise = Exercise.objects.create(workout=workout, name="Test Exercise", exercise_number=None)
        assert exercise.exercise_number is None
