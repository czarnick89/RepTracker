from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkoutViewSet, ExerciseViewSet, SetViewSet, TemplateSetViewSet, TemplateExerciseViewSet, TemplateWorkoutViewSet, exercise_gif_proxy, exercise_by_name_proxy

router = DefaultRouter()
router.register('workouts', WorkoutViewSet, basename='workout')
router.register('exercises', ExerciseViewSet)
router.register('sets', SetViewSet)
router.register('template-workouts', TemplateWorkoutViewSet, basename='templateworkout')
router.register('template-exercises', TemplateExerciseViewSet, basename='templateexercise')
router.register('template-sets', TemplateSetViewSet, basename='templateset')

urlpatterns = [
    path('', include(router.urls)),
    path('exercise-gif/', exercise_gif_proxy, name='exercise_gif_proxy'),
    path('exercise-by-name/', exercise_by_name_proxy, name = 'exercise_by_name_proxy'),
]