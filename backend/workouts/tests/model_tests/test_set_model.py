import pytest
from django.core.exceptions import ValidationError
from workouts.models import Exercise, Set, Workout
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestSetModel:
    @pytest.fixture
    def user(self):
        return User.objects.create_user(email='test@example.com', password='password')

    @pytest.fixture
    def workout(self, user):
        return Workout.objects.create(user=user, workout_number=1, date='2025-01-01', name='Test Workout')

    @pytest.fixture
    def exercise(self, workout):
        return Exercise.objects.create(workout=workout, name='Squat', exercise_number=1)

    def test_create_set(self, exercise):
        set1 = Set.objects.create(exercise=exercise, set_number=1, reps=5, weight=135)
        assert set1.set_number == 1
        assert set1.reps == 5
        assert set1.weight == 135

    def test_str_method(self, exercise):
        set1 = Set.objects.create(exercise=exercise, set_number=1, reps=8, weight=100)
        assert str(set1) == "Set 1: 8 reps @ 100.00 lbs"

    def test_unique_set_number_per_exercise(self, exercise):
        Set.objects.create(exercise=exercise, set_number=1, reps=5, weight=135)
        with pytest.raises(Exception) as excinfo:
            # Attempt to create a duplicate set_number for the same exercise
            Set.objects.create(exercise=exercise, set_number=1, reps=8, weight=150)
        assert 'unique_set_number_per_exercise' in str(excinfo.value)

    def test_same_set_number_different_exercises(self, workout):
        ex1 = Exercise.objects.create(workout=workout, name='Squat', exercise_number=1)
        ex2 = Exercise.objects.create(workout=workout, name='Bench Press', exercise_number=2)
        Set.objects.create(exercise=ex1, set_number=1, reps=5, weight=135)
        # This should be allowed because it's a different exercise
        set2 = Set.objects.create(exercise=ex2, set_number=1, reps=5, weight=100)
        assert set2.set_number == 1

    def test_ordering(self, exercise):
        Set.objects.create(exercise=exercise, set_number=2, reps=5, weight=135)
        Set.objects.create(exercise=exercise, set_number=1, reps=8, weight=100)
        sets = list(Set.objects.filter(exercise=exercise))
        assert sets[0].set_number == 1
        assert sets[1].set_number == 2
