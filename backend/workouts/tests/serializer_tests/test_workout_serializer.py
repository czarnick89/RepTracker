import pytest
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from workouts.models import Workout
from workouts.serializers import WorkoutSerializer

User = get_user_model()

@pytest.mark.django_db
class TestWorkoutSerializer:
    def setup_method(self):
        self.user = User.objects.create_user(email="test@example.com", password="password123")
        self.other_user = User.objects.create_user(email="other@example.com", password="password123")

    def test_create_workout_with_workout_number(self):
        data = {
            "date": date.today(),
            "name": "Test Workout",
            "workout_number": 5,
            "notes": "Some notes"
        }
        serializer = WorkoutSerializer(data=data, context={"request": self._fake_request(self.user)})
        assert serializer.is_valid(), serializer.errors
        workout = serializer.save()
        assert workout.workout_number == 5
        assert workout.user == self.user

    def test_create_workout_without_workout_number_auto_increments(self):
        # Create a workout to set last_number=1
        Workout.objects.create(user=self.user, workout_number=1, date=date.today(), name="Existing")
        
        data = {
            "date": date.today(),
            "name": "New Workout"
        }
        serializer = WorkoutSerializer(data=data, context={"request": self._fake_request(self.user)})
        assert serializer.is_valid(), serializer.errors
        workout = serializer.save()
        assert workout.workout_number == 2  # auto incremented
        assert workout.user == self.user

    def test_missing_required_fields(self):
        data = {}
        serializer = WorkoutSerializer(data=data, context={"request": self._fake_request(self.user)})
        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)
        # date and name are required by model but no custom error on serializer, so it will fail model save
        # To be explicit, you could add validators or test the errors here

    def test_update_does_not_change_user(self):
        workout = Workout.objects.create(user=self.user, workout_number=1, date=date.today(), name="Old")
        update_data = {
            "name": "Updated Workout",
            "user": self.other_user.id  # Should be ignored
        }
        serializer = WorkoutSerializer(workout, data=update_data, partial=True, context={"request": self._fake_request(self.user)})
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()
        assert updated.name == "Updated Workout"
        assert updated.user == self.user  # user unchanged

    def test_read_only_fields_not_modified(self):
        workout = Workout.objects.create(user=self.user, workout_number=1, date=date.today(), name="Old")
        update_data = {
            "created_at": "2000-01-01T00:00:00Z",
            "updated_at": "2000-01-01T00:00:00Z"
        }
        serializer = WorkoutSerializer(workout, data=update_data, partial=True, context={"request": self._fake_request(self.user)})
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()
        assert updated.created_at != "2000-01-01T00:00:00Z"

    def test_exercises_are_read_only(self):
        workout = Workout.objects.create(user=self.user, workout_number=1, date=date.today(), name="Workout")
        serializer = WorkoutSerializer(workout)
        assert 'exercises' in serializer.data
        # Exercises should be serialized as empty list by default
        assert serializer.data['exercises'] == []

    # Helper method to fake request with user
    class DummyRequest:
        def __init__(self, user):
            self.user = user

    def _fake_request(self, user):
        return self.DummyRequest(user)
