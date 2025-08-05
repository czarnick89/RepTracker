import pytest
from datetime import date, timedelta
from workouts.models import Workout
from django.db import IntegrityError

@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(email="test@example.com", password="testpass123")

@pytest.mark.django_db
class TestWorkoutModel:

    def test_create_workout(self, user):
        workout = Workout.objects.create(
            user=user,
            workout_number=1,
            date=date.today(),
            name="Push Day",
            notes="Felt strong today"
        )
        assert workout.name == "Push Day"
        assert workout.notes == "Felt strong today"
        assert workout.user == user

    def test_str_method(self, user):
        workout = Workout.objects.create(
            user=user,
            workout_number=2,
            date=date(2025, 8, 5),
            name="Pull Day"
        )
        expected = "Workout 2 - Pull Day (2025-08-05)"
        assert str(workout) == expected

    def test_ordering(self, user):
        w1 = Workout.objects.create(user=user, workout_number=1, date=date.today(), name="A")
        w2 = Workout.objects.create(user=user, workout_number=2, date=date.today() - timedelta(days=1), name="B")
        w3 = Workout.objects.create(user=user, workout_number=3, date=date.today(), name="C")
        workouts = list(Workout.objects.filter(user=user))
        assert workouts == [w1, w3, w2]  # Ordered by -date, then workout_number

    def test_unique_workout_number_constraint(self, user):
        Workout.objects.create(user=user, workout_number=1, date=date.today(), name="Leg Day")
        with pytest.raises(IntegrityError):
            Workout.objects.create(user=user, workout_number=1, date=date.today(), name="Chest Day")
