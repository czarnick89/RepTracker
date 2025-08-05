import pytest
from workouts.models import Set, Exercise, Workout
from workouts.serializers import SetSerializer
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

@pytest.mark.django_db
class TestSetSerializer:

    def setup_method(self):
        self.user = User.objects.create_user(email="test@example.com", password="password")
        self.workout = Workout.objects.create(user=self.user, workout_number=1, date=date.today(), name="Test Workout")
        self.exercise = Exercise.objects.create(workout=self.workout, name="Bench Press", exercise_number=1)

    def test_valid_input_with_set_number(self):
        data = {
            "exercise": self.exercise.id,
            "set_number": 1,
            "reps": 10,
            "weight": 135
        }
        serializer = SetSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        set_instance = serializer.save()
        assert set_instance.set_number == 1
        assert set_instance.reps == 10
        assert set_instance.weight == 135
        assert set_instance.exercise == self.exercise

    def test_valid_input_without_set_number(self):
        # First, create a set manually to simulate existing one
        Set.objects.create(exercise=self.exercise, set_number=1, reps=8, weight=135)
        
        data = {
            "exercise": self.exercise.id,
            "reps": 6,
            "weight": 145
        }
        serializer = SetSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        set_instance = serializer.save()
        assert set_instance.set_number == 2  # auto-incremented
        assert set_instance.reps == 6

    def test_missing_exercise_raises_error(self):
        data = {
            "set_number": 1,
            "reps": 10,
            "weight": 135
        }
        serializer = SetSerializer(data=data)
        assert not serializer.is_valid()
        assert "exercise" in serializer.errors

    def test_update_does_not_allow_exercise_change(self):
        set_instance = Set.objects.create(exercise=self.exercise, set_number=1, reps=10, weight=135)
        new_exercise = Exercise.objects.create(workout=self.workout, name="Incline Press", exercise_number=2)

        update_data = {
            "exercise": new_exercise.id,  # Should be ignored
            "reps": 12,
            "weight": 150
        }

        serializer = SetSerializer(instance=set_instance, data=update_data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated_set = serializer.save()
        assert updated_set.exercise == self.exercise  # Still original
        assert updated_set.reps == 12
        assert updated_set.weight == 150
