import pytest
from django.db import IntegrityError
from workouts.models import TemplateWorkout, TemplateExercise
from workouts.serializers import TemplateExerciseSerializer

@pytest.mark.django_db
class TestTemplateExerciseSerializer:

    @pytest.fixture
    def user(self, django_user_model):
        return django_user_model.objects.create_user(email="testuser@example.com", password="pass123")

    @pytest.fixture
    def template_workout(self, user):
        return TemplateWorkout.objects.create(user=user, template_number=1, name="Template 1")

    def test_valid_input_with_exercise_number(self, template_workout):
        data = {
            "workout_template": template_workout.id,
            "name": "Exercise 1",
            "exercise_number": 1
        }
        serializer = TemplateExerciseSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        assert instance.name == "Exercise 1"
        assert instance.exercise_number == 1
        assert instance.workout_template == template_workout

    def test_valid_input_without_exercise_number_auto_increment(self, template_workout):
        # Pre-create one exercise to set exercise_number=1
        TemplateExercise.objects.create(workout_template=template_workout, name="Ex 1", exercise_number=1)

        data = {
            "workout_template": template_workout.id,
            "name": "Exercise 2"
        }
        serializer = TemplateExerciseSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        assert instance.exercise_number == 2  # auto incremented

    def test_missing_workout_template_raises_validation_error(self):
        data = {
            "name": "No Template Exercise"
        }
        serializer = TemplateExerciseSerializer(data=data)
        with pytest.raises(Exception) as exc:
            serializer.is_valid(raise_exception=True)
        assert 'workout_template' in str(exc.value)

    def test_update_does_not_allow_changing_workout_template(self, template_workout):
        instance = TemplateExercise.objects.create(workout_template=template_workout, name="Original", exercise_number=1)
        new_template = TemplateWorkout.objects.create(user=template_workout.user, template_number=2, name="New Template")

        update_data = {
            "workout_template": new_template.id,  # Should be ignored
            "name": "Updated Name"
        }
        serializer = TemplateExerciseSerializer(instance, data=update_data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()
        assert updated.name == "Updated Name"
        assert updated.workout_template == template_workout  # Should not change

    def test_read_only_fields_are_not_modified(self, template_workout):
        instance = TemplateExercise.objects.create(workout_template=template_workout, name="ReadOnlyTest", exercise_number=1)
        update_data = {
            "created_at": "2000-01-01T00:00:00Z",
            "updated_at": "2000-01-01T00:00:00Z"
        }
        serializer = TemplateExerciseSerializer(instance, data=update_data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()
        assert updated.created_at.isoformat() != "2000-01-01T00:00:00+00:00"

    def test_required_fields_validation(self):
        """Test that workout_template and name are required."""
        # Missing workout_template
        data = {
            "name": "Exercise without template"
        }
        serializer = TemplateExerciseSerializer(data=data)
        assert not serializer.is_valid()
        assert "workout_template" in serializer.errors

        # Missing name
        data = {
            "workout_template": 1
        }
        serializer = TemplateExerciseSerializer(data=data)
        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_exercise_number_uniqueness_within_template(self, template_workout):
        """Test that exercise_number must be unique within a template workout."""
        # Create first exercise
        TemplateExercise.objects.create(workout_template=template_workout, name="Bench Press", exercise_number=1)

        # Try to create another with same exercise_number in same template - should fail
        data = {
            "workout_template": template_workout.id,
            "name": "Incline Press",
            "exercise_number": 1  # Same number - should fail validation
        }
        serializer = TemplateExerciseSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors  # Unique constraint violation

    def test_exercise_number_can_be_null(self, template_workout):
        """Test that exercise_number can be null."""
        data = {
            "workout_template": template_workout.id,
            "name": "Exercise with null number"
        }
        serializer = TemplateExerciseSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        assert instance.exercise_number == 1  # Should auto-assign 1

    def test_name_field_validation(self, template_workout):
        """Test name field validation."""
        # Valid name
        data = {
            "workout_template": template_workout.id,
            "name": "Valid Exercise Name"
        }
        serializer = TemplateExerciseSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        # Empty name should fail
        data_empty = {
            "workout_template": template_workout.id,
            "name": ""
        }
        serializer = TemplateExerciseSerializer(data=data_empty)
        assert not serializer.is_valid()
        assert "name" in serializer.errors
