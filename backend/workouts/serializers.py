from rest_framework import serializers
from .models import Set, Exercise, Workout, TemplateSet, TemplateExercise, TemplateWorkout
from django.db import models
from django.db.models import Max
from django.core.exceptions import ValidationError as DjangoValidationError

class SetSerializer(serializers.ModelSerializer):
    set_number = serializers.IntegerField(required=False)

    class Meta:
        model = Set
        fields = ['id', 'exercise', 'set_number', 'reps', 'weight', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def run_validators(self, value):
        # Skip UniqueTogetherValidator if set_number is not yet computed
        if self.instance is None and ('set_number' not in self.initial_data or self.initial_data['set_number'] in [None, '']):
            return  # Skip default validators
        return super().run_validators(value)

    def validate(self, attrs):
        if self.instance is None:
            exercise = attrs.get('exercise')
            if not exercise:
                raise serializers.ValidationError({'exercise': 'This field is required.'})

            if 'set_number' not in attrs or attrs['set_number'] is None:
                last_number = (
                    Set.objects.filter(exercise=exercise)
                    .aggregate(models.Max('set_number'))['set_number__max'] or 0
                )
                attrs['set_number'] = last_number + 1

        return attrs

    def update(self, instance, validated_data):
        validated_data.pop('exercise', None)
        return super().update(instance, validated_data)
    
    def validate_weight(self, value):
        if value < 0:
            raise serializers.ValidationError("Weight must be zero or positive.")
        return value


class ExerciseSerializer(serializers.ModelSerializer):
    sets = SetSerializer(many=True, read_only=True)
    exercise_number = serializers.IntegerField(required=False)  # optional on input

    class Meta:
        model = Exercise
        fields = ['id', 'workout', 'name', 'exercise_number', 'weight_change_preference', 'sets', 'created_at', 'updated_at']
        read_only_fields = ['id', 'sets', 'created_at', 'updated_at']
        validators = []  # Disable UniqueTogetherValidator added by DRF automatically

    def validate(self, attrs):
        if self.instance is None:
            workout = attrs.get('workout')
            if not workout:
                raise serializers.ValidationError({'workout': 'This field is required.'})

            if 'exercise_number' not in attrs or attrs['exercise_number'] is None:
                last_number = (
                    Exercise.objects.filter(workout=workout)
                    .aggregate(Max('exercise_number'))['exercise_number__max'] or 0
                )
                attrs['exercise_number'] = last_number + 1

            # Manually check uniqueness after assignment
            if Exercise.objects.filter(workout=workout, exercise_number=attrs['exercise_number']).exists():
                raise serializers.ValidationError({
                    'exercise_number': 'This exercise number already exists for this workout.'
                })

        return attrs

    def update(self, instance, validated_data):
        validated_data.pop('workout', None)  # prevent workout change
        return super().update(instance, validated_data)

class WorkoutSerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True, read_only=True)
    workout_number = serializers.IntegerField(required=False)

    class Meta:
        model = Workout
        fields = ['id', 'user', 'workout_number', 'date', 'name', 'notes', 'exercises', 'created_at', 'updated_at']
        read_only_fields = ['user', 'id', 'created_at', 'updated_at']

    def validate(self, attrs):
        if self.instance is None:
            # We're creating a new Workout
            user = self.context['request'].user
            if 'workout_number' not in attrs or attrs['workout_number'] is None:
                last_number = (
                    Workout.objects.filter(user=user)
                    .aggregate(models.Max('workout_number'))['workout_number__max'] or 0
                )
                attrs['workout_number'] = last_number + 1

        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('user', None)
        return super().update(instance, validated_data)
    
class TemplateSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateSet
        fields = ['id', 'exercise', 'set_number', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        validated_data.pop('exercise', None)  # prevent changing exercise on update
        return super().update(instance, validated_data)

class TemplateExerciseSerializer(serializers.ModelSerializer):
    exercise_number = serializers.IntegerField(required=False, allow_null=True, default=None)
    workout_template = serializers.PrimaryKeyRelatedField(queryset=TemplateWorkout.objects.all())
    sets = TemplateSetSerializer(many=True, read_only=True)

    class Meta:
        model = TemplateExercise
        fields = ['id', 'workout_template', 'name', 'exercise_number', 'sets', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']  # FIXED: removed 'workout_template'

    def validate(self, attrs):
        if self.instance is None:  # creation
            workout_template = attrs.get('workout_template')
            if not workout_template:
                raise serializers.ValidationError({'workout_template': 'This field is required.'})

            if 'exercise_number' not in attrs or attrs['exercise_number'] is None:
                last_number = (
                    TemplateExercise.objects
                    .filter(workout_template=workout_template)
                    .aggregate(models.Max('exercise_number'))['exercise_number__max'] or 0
                )
                attrs['exercise_number'] = last_number + 1
        return attrs

    def update(self, instance, validated_data):
        validated_data.pop('workout_template', None)  # prevent FK from being updated
        return super().update(instance, validated_data)

class TemplateWorkoutSerializer(serializers.ModelSerializer):
    template_number = serializers.IntegerField(required=False, allow_null=True, default=None)
    exercises = TemplateExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = TemplateWorkout
        fields = ['id', 'user', 'template_number', 'name', 'description', 'exercises', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, attrs):
        user = self.context['request'].user if 'request' in self.context else None
        if user is None:
            raise serializers.ValidationError({'user': 'User context is required.'})

        if self.instance is None:
            # Creating new instance
            template_number = attrs.get('template_number')

            # Auto-increment if not provided
            if template_number is None:
                last_number = (
                    TemplateWorkout.objects.filter(user=user)
                    .aggregate(models.Max('template_number'))['template_number__max'] or 0
                )
                template_number = last_number + 1
                attrs['template_number'] = template_number

            # Check uniqueness manually
            if TemplateWorkout.objects.filter(user=user, template_number=template_number).exists():
                raise serializers.ValidationError({'template_number': 'This template number is already in use for this user.'})

        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('user', None)
        return super().update(instance, validated_data)