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

    # Helper to create a TemplateWorkout for FK
    def _create_template_workout(self):
        from workouts.models import TemplateWorkout
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(email="testuser@example.com", password="pass1234")
        return TemplateWorkout.objects.create(user=user, template_number=1, name="Template Workout")
