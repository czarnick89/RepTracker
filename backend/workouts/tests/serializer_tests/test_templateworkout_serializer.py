import pytest
from workouts.models import TemplateWorkout
from workouts.serializers import TemplateWorkoutSerializer
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

User = get_user_model()

@pytest.mark.django_db
class TestTemplateWorkoutSerializer:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user = User.objects.create_user(email="test@example.com", password="password123")

    def get_serializer_context(self):
        # Simulate request user in serializer context
        class DummyRequest:
            def __init__(self, user):
                self.user = user
        return {'request': DummyRequest(self.user)}

    def test_valid_input_with_template_number(self):
        data = {
            "template_number": 5,
            "name": "Full Body Template",
            "description": "A full body workout template"
        }
        serializer = TemplateWorkoutSerializer(data=data, context=self.get_serializer_context())
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        assert instance.template_number == 5
        assert instance.name == "Full Body Template"
        assert instance.user == self.user

    def test_valid_input_without_template_number_autoincrement(self):
        # Create one template with number 1
        TemplateWorkout.objects.create(user=self.user, template_number=1, name="Existing Template")

        data = {
            "name": "New Template",
            "description": "New description"
        }
        serializer = TemplateWorkoutSerializer(data=data, context=self.get_serializer_context())
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        assert instance.template_number == 2  # Auto-incremented
        assert instance.user == self.user

    def test_missing_user_in_context_raises_error(self):
        data = {
            "name": "Template Without User"
        }
        serializer = TemplateWorkoutSerializer(data=data, context={})  # no user in context
        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)
        assert 'user' in str(exc.value)

    def test_read_only_fields_not_modified(self):
        tw = TemplateWorkout.objects.create(user=self.user, template_number=1, name="Template 1")

        update_data = {
            "user": None,
            "created_at": "2000-01-01T00:00:00Z",
            "updated_at": "2000-01-01T00:00:00Z",
            "name": "Updated Template"
        }
        serializer = TemplateWorkoutSerializer(tw, data=update_data, partial=True, context=self.get_serializer_context())
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()
        assert updated.name == "Updated Template"
        assert updated.user == self.user  # user not changed

    def test_required_fields_validation(self):
        """Test that name is required."""
        data = {
            "description": "Template without name"
        }
        serializer = TemplateWorkoutSerializer(data=data, context=self.get_serializer_context())
        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_description_field_optional(self):
        """Test that description field is optional."""
        data = {
            "name": "Template without description"
        }
        serializer = TemplateWorkoutSerializer(data=data, context=self.get_serializer_context())
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        assert instance.description == ""  # Should be blank

        # Test with description
        data_with_desc = {
            "name": "Template with description",
            "description": "This is a comprehensive workout template."
        }
        serializer = TemplateWorkoutSerializer(data=data_with_desc, context=self.get_serializer_context())
        assert serializer.is_valid(), serializer.errors
        instance_with_desc = serializer.save()
        assert instance_with_desc.description == "This is a comprehensive workout template."

    def test_template_number_uniqueness_per_user(self):
        """Test that template_number must be unique per user."""
        # Create first template
        TemplateWorkout.objects.create(user=self.user, template_number=1, name="First Template")

        # Try to create another with same template_number for same user - should fail
        data = {
            "name": "Second Template",
            "template_number": 1  # Same number - should fail validation
        }
        serializer = TemplateWorkoutSerializer(data=data, context=self.get_serializer_context())
        assert not serializer.is_valid()
        assert "template_number" in serializer.errors

    def test_name_field_validation(self):
        """Test name field validation."""
        # Valid name
        data = {
            "name": "Valid Template Name"
        }
        serializer = TemplateWorkoutSerializer(data=data, context=self.get_serializer_context())
        assert serializer.is_valid(), serializer.errors

        # Empty name should fail
        data_empty = {
            "name": ""
        }
        serializer = TemplateWorkoutSerializer(data=data_empty, context=self.get_serializer_context())
        assert not serializer.is_valid()
        assert "name" in serializer.errors
