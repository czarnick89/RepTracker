from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkoutViewSet, ExerciseViewSet, SetViewSet, TemplateSetViewSet, TemplateExerciseViewSet, TemplateWorkoutViewSet, exercise_gif_proxy, exercise_by_name_proxy, google_calendar_auth_start, google_calendar_oauth2callback, add_workout_to_calendar, google_calendar_status, google_calendar_disconnect

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
    path('google-calendar/auth-start/', google_calendar_auth_start, name = 'google_calendar_auth_start'),
    path('google-calendar/oauth2callback', google_calendar_oauth2callback, name='google_calendar_oauth2callback'),
    path('google-calendar/create-event/', add_workout_to_calendar, name='add_workout_to_calendar'),
    path('google-calendar/status/', google_calendar_status, name='google_calendar_status'),
    path('google-calendar/disconnect/', google_calendar_disconnect, name='google_calendar_disconnect'),
    
]