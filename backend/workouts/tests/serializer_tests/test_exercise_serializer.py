import pytest
from workouts.models import Workout, Exercise
from workouts.serializers import ExerciseSerializer
from users.models import User
from rest_framework.exceptions import ValidationError
from datetime import date

@pytest.mark.django_db
class TestExerciseSerializer:
    def setup_method(self):
        self.user = User.objects.create_user(email="test@example.com", password="password123")
        self.workout = Workout.objects.create(
            user=self.user,
            name="Push Day",
            workout_number=1,
            date=date.today()
        )

    def test_valid_input_with_exercise_number(self):
        data = {
            "workout": self.workout.id,
            "name": "Bench Press",
            "exercise_number": 1,
            "weight_change_preference": "increase"
        }
        serializer = ExerciseSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        assert instance.exercise_number == 1
        assert instance.name == "Bench Press"
        assert instance.workout == self.workout
        assert instance.weight_change_preference == "increase"

    def test_valid_input_without_exercise_number(self):
        # Pre-populate one exercise
        Exercise.objects.create(workout=self.workout, name="Bench Press", exercise_number=1)

        data = {
            "workout": self.workout.id,
            "name": "Incline Dumbbell Press",
            "weight_change_preference": "decrease"
        }
        serializer = ExerciseSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        assert instance.exercise_number == 2  # Auto-incremented
        assert instance.name == "Incline Dumbbell Press"
        assert instance.weight_change_preference == "decrease"

    def test_default_weight_change_preference(self):
        data = {
            "workout": self.workout.id,
            "name": "Deadlift",
            "exercise_number": 3,
            # weight_change_preference omitted to test default
        }
        serializer = ExerciseSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        assert instance.weight_change_preference == "same"  # Default value

    def test_missing_workout_raises_validation_error(self):
        data = {
            "name": "Bench Press"
        }
        serializer = ExerciseSerializer(data=data)
        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)
        assert "workout" in exc.value.detail

    def test_update_does_not_allow_changing_workout(self):
        exercise = Exercise.objects.create(workout=self.workout, name="Bench Press", exercise_number=1)
        new_workout = Workout.objects.create(
            user=self.user,
            name="New Workout",
            workout_number=2,
            date=date.today()
        )

        update_data = {
            "workout": new_workout.id,  # Should be ignored
            "name": "Updated Press",
            "weight_change_preference": "increase"
        }
        serializer = ExerciseSerializer(exercise, data=update_data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()
        assert updated.name == "Updated Press"
        assert updated.workout == self.workout  # Not changed
        assert updated.weight_change_preference == "increase"

    def test_read_only_fields_are_not_modified(self):
        exercise = Exercise.objects.create(workout=self.workout, name="Bench Press", exercise_number=1)

        update_data = {
            "created_at": "2000-01-01T00:00:00Z",  # Should be ignored
            "updated_at": "2000-01-01T00:00:00Z"
        }
        serializer = ExerciseSerializer(exercise, data=update_data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()
        assert updated.created_at != "2000-01-01T00:00:00Z"