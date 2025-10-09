import pytest
from workouts.models import TemplateSet, TemplateExercise
from workouts.serializers import TemplateSetSerializer

@pytest.mark.django_db
class TestTemplateSetSerializer:
    def setup_method(self):
        # Create a TemplateExercise to associate TemplateSets with
        self.template_exercise = TemplateExercise.objects.create(
            workout_template=self._create_template_workout(),
            name="Test Exercise",
            exercise_number=1
        )

    def test_create_template_set(self):
        data = {
            "exercise": self.template_exercise.id,
            "set_number": 1
        }
        serializer = TemplateSetSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        assert instance.set_number == 1
        assert instance.exercise == self.template_exercise

    def test_read_only_fields_not_modified_on_update(self):
        # Setup: create TemplateSet with exercise
        template_set = TemplateSet.objects.create(exercise=self.template_exercise, set_number=1)

        # Update payload without exercise field
        update_data = {
            "set_number": 2,  # change allowed field
        }
        serializer = TemplateSetSerializer(template_set, data=update_data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()
        assert updated.set_number == 2
        # exercise should remain unchanged
        assert updated.exercise == self.template_exercise

    def test_required_fields_validation(self):
        """Test that exercise is required."""
        data = {
            "set_number": 1
        }
        serializer = TemplateSetSerializer(data=data)
        assert not serializer.is_valid()
        assert "exercise" in serializer.errors

    def test_set_number_auto_assignment(self):
        """Test that set_number is required and validated."""
        # Valid set_number
        data = {
            "exercise": self.template_exercise.id,
            "set_number": 1
        }
        serializer = TemplateSetSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        # Missing set_number should fail
        data_no_number = {
            "exercise": self.template_exercise.id
        }
        serializer = TemplateSetSerializer(data=data_no_number)
        assert not serializer.is_valid()
        assert "set_number" in serializer.errors

    def test_update_prevents_exercise_change(self):
        """Test that exercise cannot be changed on update."""
        template_set = TemplateSet.objects.create(exercise=self.template_exercise, set_number=1)

        # Create another exercise
        other_exercise = TemplateExercise.objects.create(
            workout_template=self.template_exercise.workout_template,
            name="Other Exercise",
            exercise_number=2
        )

        update_data = {
            "exercise": other_exercise.id,  # Should be ignored
            "set_number": 2
        }
        serializer = TemplateSetSerializer(template_set, data=update_data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()
        assert updated.exercise == self.template_exercise  # Should not change
        assert updated.set_number == 2

    def test_read_only_fields_protection(self):
        """Test that created_at and updated_at are read-only."""
        template_set = TemplateSet.objects.create(exercise=self.template_exercise, set_number=1)

        update_data = {
            "created_at": "2000-01-01T00:00:00Z",
            "updated_at": "2000-01-01T00:00:00Z"
        }
        serializer = TemplateSetSerializer(template_set, data=update_data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()
        # Timestamps should not be changed to the fake values
        assert updated.created_at != "2000-01-01T00:00:00Z"

    # Helper to create a TemplateWorkout for FK
    def _create_template_workout(self):
        from workouts.models import TemplateWorkout
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(email="testuser@example.com", password="pass1234")
        return TemplateWorkout.objects.create(user=user, template_number=1, name="Template Workout")
