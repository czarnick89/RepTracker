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

    def test_notes_field_blank(self, user):
        """Test that notes field can be blank."""
        workout = Workout.objects.create(
            user=user,
            workout_number=1,
            date=date.today(),
            name="Test Workout"
        )
        assert workout.notes == ""

    def test_notes_field_with_content(self, user):
        """Test notes field with actual content."""
        notes_content = "Felt great today! PR on bench press."
        workout = Workout.objects.create(
            user=user,
            workout_number=1,
            date=date.today(),
            name="Test Workout",
            notes=notes_content
        )
        assert workout.notes == notes_content

    def test_workout_number_positive_integer(self, user):
        """Test that workout_number must be positive."""
        # Valid positive number
        workout = Workout.objects.create(
            user=user,
            workout_number=5,
            date=date.today(),
            name="Test Workout"
        )
        assert workout.workout_number == 5

        # Zero should be allowed (though not practical)
        workout2 = Workout.objects.create(
            user=user,
            workout_number=0,
            date=date.today() - timedelta(days=1),
            name="Test Workout 2"
        )
        assert workout2.workout_number == 0

    def test_date_field_validation(self, user):
        """Test date field accepts valid dates."""
        from datetime import date
        workout = Workout.objects.create(
            user=user,
            workout_number=1,
            date=date(2025, 12, 25),
            name="Christmas Workout"
        )
        assert workout.date == date(2025, 12, 25)

    def test_name_field_max_length(self, user):
        """Test name field max_length constraint."""
        # Valid length
        workout = Workout.objects.create(
            user=user,
            workout_number=1,
            date=date.today(),
            name="A" * 100  # Exactly max length
        )
        assert len(workout.name) == 100

        # Test that shorter names work too
        workout2 = Workout.objects.create(
            user=user,
            workout_number=2,
            date=date.today(),
            name="Short name"
        )
        assert workout2.name == "Short name"
