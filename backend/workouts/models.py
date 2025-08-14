from django.db import models
from django.conf import settings

class Workout(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workouts'
    )
    workout_number = models.PositiveIntegerField()
    date = models.DateField()
    name = models.CharField(max_length=100)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'workout_number']
        constraints = [
            models.UniqueConstraint(fields=['user', 'workout_number'], name='unique_workout_number_per_user')
        ]

    def __str__(self):
        return f"Workout {self.workout_number} - {self.name} ({self.date})"

class Exercise(models.Model):

    WEIGHT_CHANGE_CHOICES = [
        ('increase', 'Increase Weight'),
        ('decrease', 'Decrease Weight'),
        ('same', 'Maintain Weight'),
    ]

    workout = models.ForeignKey(
        'Workout',
        on_delete=models.CASCADE,
        related_name='exercises'
    )
    name = models.CharField(max_length=100)
    exercise_number = models.PositiveIntegerField(null=True, blank=True)

    weight_change_preference = models.CharField(
        max_length=8,
        choices=WEIGHT_CHANGE_CHOICES,
        default='same',
        help_text="User preference for weight change on this exercise"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['exercise_number']
        constraints = [
            models.UniqueConstraint(fields=['workout', 'exercise_number'], name='unique_exercise_number_per_workout')
        ]

    def __str__(self):
        return f"Exercise {self.exercise_number}: {self.name} (Workout ID: {self.workout_id})"

class Set(models.Model):
    exercise = models.ForeignKey(
        'Exercise',
        on_delete=models.CASCADE,
        related_name='sets'
    )
    set_number = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=6, decimal_places=2) 

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['set_number']  # ensures sets show up in logical order
        constraints = [
            models.UniqueConstraint(fields=['exercise', 'set_number'], name='unique_set_number_per_exercise')
        ]

    def __str__(self):
        return f"Set {self.set_number}: {self.reps} reps @ {self.weight:.2f} lbs"
    
class TemplateWorkout(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workout_templates')
    template_number = models.PositiveIntegerField()
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'template_number'], name='unique_template_number_per_user')
        ]
        ordering = ['template_number']

    def __str__(self):
        return f"Template '{self.name}' by {self.user.email}"

class TemplateExercise(models.Model):
    workout_template = models.ForeignKey(TemplateWorkout, on_delete=models.CASCADE, related_name='exercises')
    name = models.CharField(max_length=100)
    exercise_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['exercise_number']
        constraints = [
            models.UniqueConstraint(fields=['workout_template', 'exercise_number'], name='unique_exercise_number_per_template')
        ]

    def __str__(self):
        return f"Template Exercise {self.exercise_number}: {self.name}"

class TemplateSet(models.Model):
    exercise = models.ForeignKey(TemplateExercise, on_delete=models.CASCADE, related_name='sets')
    set_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['set_number']
        constraints = [
            models.UniqueConstraint(
                fields=['exercise', 'set_number'], 
                name='unique_templateset_set_number_per_exercise'
            )
        ]

    def __str__(self):
        return f"Template Set {self.set_number} for Exercise {self.exercise_id}"