from django.contrib import admin
from .models import Workout, Exercise, Set

class SetInline(admin.TabularInline):  # could also use StackedInline
    model = Set
    extra = 1  # number of empty forms to show

class ExerciseInline(admin.TabularInline):
    model = Exercise
    extra = 1

# Workout admin: shows Exercises inline
@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'date', 'workout_number')
    list_filter = ('date', 'user')
    search_fields = ('name',)
    ordering = ('-date', 'workout_number')
    inlines = [ExerciseInline]  # edit Exercises right in Workout page

# Exercise admin: shows Sets inline
@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('id', 'workout', 'name', 'exercise_number', 'weight_change_preference')
    list_filter = ('weight_change_preference',)
    search_fields = ('name',)
    ordering = ('workout', 'exercise_number')
    inlines = [SetInline]  # edit Sets right in Exercise page

# Set admin stays as is
@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ('id', 'exercise', 'set_number', 'reps', 'weight')
    ordering = ('exercise', 'set_number')
