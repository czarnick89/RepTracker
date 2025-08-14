from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WorkoutViewSet,
    ExerciseViewSet,
    SetViewSet,
    TemplateSetViewSet,
    TemplateExerciseViewSet,
    TemplateWorkoutViewSet,
    ExerciseGifProxy,
    ExerciseByNameProxy,
    GoogleCalendarAuthStart,
    GoogleCalendarOAuth2Callback,
    AddWorkoutToCalendar,
    GoogleCalendarStatus,
    GoogleCalendarDisconnect,
)

router = DefaultRouter()
router.register('workouts', WorkoutViewSet, basename='workout')
router.register('exercises', ExerciseViewSet)
router.register('sets', SetViewSet)
router.register('template-workouts', TemplateWorkoutViewSet, basename='templateworkout')
router.register('template-exercises', TemplateExerciseViewSet, basename='templateexercise')
router.register('template-sets', TemplateSetViewSet, basename='templateset')

urlpatterns = [
    path('', include(router.urls)),
    path('exercise-gif/', ExerciseGifProxy.as_view(), name='exercise_gif_proxy'),
    path('exercise-by-name/', ExerciseByNameProxy.as_view(), name='exercise_by_name_proxy'),
    path('google-calendar/auth-start/', GoogleCalendarAuthStart.as_view(), name='google_calendar_auth_start'),
    path('google-calendar/oauth2callback/', GoogleCalendarOAuth2Callback.as_view(), name='google_calendar_oauth2callback'),
    path('google-calendar/create-event/', AddWorkoutToCalendar.as_view(), name='add_workout_to_calendar'),
    path('google-calendar/status/', GoogleCalendarStatus.as_view(), name='google_calendar_status'),
    path('google-calendar/disconnect/', GoogleCalendarDisconnect.as_view(), name='google_calendar_disconnect'),
]
