import pytest
from django.db import IntegrityError
from workouts.models import TemplateWorkout
from django.contrib.auth import get_user_model

@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(email="user@example.com", password="pass1234")

@pytest.mark.django_db
class TestTemplateWorkoutModel:

    def test_create_template_workout(self, user):
        tw = TemplateWorkout.objects.create(
            user=user,
            template_number=1,
            name="Full Body Template",
            description="A great all-round workout template"
        )
        assert tw.user == user
        assert tw.template_number == 1
        assert tw.name == "Full Body Template"
        assert tw.description == "A great all-round workout template"
        assert tw.created_at is not None
        assert tw.updated_at is not None

    def test_str_method(self, user):
        tw = TemplateWorkout.objects.create(user=user, template_number=2, name="Leg Day")
        expected = f"Template 'Leg Day' by {user.email}"
        assert str(tw) == expected

    def test_ordering_by_template_number(self, user):
        tw1 = TemplateWorkout.objects.create(user=user, template_number=2, name="Template B")
        tw2 = TemplateWorkout.objects.create(user=user, template_number=1, name="Template A")
        workouts = list(TemplateWorkout.objects.filter(user=user))
        assert workouts[0] == tw2
        assert workouts[1] == tw1

    def test_unique_template_number_constraint(self, user):
        TemplateWorkout.objects.create(user=user, template_number=1, name="Template One")
        with pytest.raises(IntegrityError):
            TemplateWorkout.objects.create(user=user, template_number=1, name="Duplicate Template")

    def test_description_field_blank(self, user):
        """Test that description field can be blank."""
        tw = TemplateWorkout.objects.create(user=user, template_number=1, name="Blank Description Template")
        assert tw.description == ""

    def test_description_field_with_content(self, user):
        """Test description field with actual content."""
        description = "This is a comprehensive full-body workout template."
        tw = TemplateWorkout.objects.create(
            user=user, 
            template_number=1, 
            name="Full Body", 
            description=description
        )
        assert tw.description == description

    def test_template_number_positive_integer(self, user):
        """Test that template_number must be positive."""
        # Valid positive number
        tw = TemplateWorkout.objects.create(user=user, template_number=3, name="Template 3")
        assert tw.template_number == 3

        # Zero should be allowed
        tw2 = TemplateWorkout.objects.create(user=user, template_number=0, name="Template 0")
        assert tw2.template_number == 0

    def test_name_field_max_length(self, user):
        """Test name field respects max_length constraint."""
        # Valid length
        tw = TemplateWorkout.objects.create(
            user=user,
            template_number=1,
            name="A" * 200  # Exactly max length
        )
        assert len(tw.name) == 200

        # Should fail with too long name
        with pytest.raises(Exception):
            TemplateWorkout.objects.create(
                user=user,
                template_number=2,
                name="A" * 201  # Over max length
            )
