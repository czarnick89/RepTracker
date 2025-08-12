from rest_framework import viewsets, permissions, status as s
from rest_framework.exceptions import PermissionDenied
from .models import Set, Exercise, Workout, TemplateSet, TemplateExercise, TemplateWorkout
from .serializers import SetSerializer, ExerciseSerializer, WorkoutSerializer, TemplateSetSerializer, TemplateExerciseSerializer, TemplateWorkoutSerializer
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Prefetch
import requests
from django.conf import settings
from django.http import HttpResponse
from decouple import config

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def exercise_by_name_proxy(request):
    name = request.query_params.get('name')
    if not name:
        return Response({"detail": "Missing 'name' parameter"}, status=s.HTTP_400_BAD_REQUEST)

    url = f"https://exercisedb.p.rapidapi.com/exercises/name/{name}"
    headers = {
        "X-RapidAPI-Key": config('RAPIDAPI_KEY'),
        "X-RapidAPI-Host": "exercisedb.p.rapidapi.com",
    }

    resp = requests.get(url, headers=headers)

    if resp.status_code != 200:
        return Response({"detail": "Failed to fetch exercise from external API"}, status=resp.status_code)

    return Response(resp.json())

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def exercise_gif_proxy(request):

    #permission_classes = [permissions.IsAuthenticated] # for some reason you cant do this in a function body

    exercise_db_id = request.query_params.get('exerciseId')
    resolution = request.query_params.get('resolution', '180')

    if not exercise_db_id:
        return HttpResponse("Missing 'exerciseId' parameter", status=400)

    url = "https://exercisedb.p.rapidapi.com/image"
    params = {
        "exerciseId": exercise_db_id,
        "resolution": resolution,
    }
    headers = {
        "X-RapidAPI-Key": config('RAPIDAPI_KEY'),
        "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
    }

    resp = requests.get(url, headers=headers, params=params)

    if resp.status_code != 200:
        return HttpResponse("Image not found", status=resp.status_code)

    return HttpResponse(resp.content, content_type=resp.headers.get("Content-Type", "image/gif"))

# Create your views here.
class SetViewSet(viewsets.ModelViewSet):
    queryset = Set.objects.all()
    serializer_class = SetSerializer
    permission_classes = [permissions.IsAuthenticated]

class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

class WorkoutViewSet(viewsets.ModelViewSet):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Workout.objects
            .filter(user=self.request.user)
            .order_by('-date', '-workout_number')  # newest first
            .prefetch_related(
                Prefetch(
                    'exercises',
                    queryset=Exercise.objects.prefetch_related('sets')
                )
            )
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        workouts = self.get_queryset()[:10]
        serializer = self.get_serializer(workouts, many=True)
        return Response(serializer.data)

class TemplateSetViewSet(viewsets.ModelViewSet):
    queryset = TemplateSet.objects.all()
    serializer_class = TemplateSetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Optionally filter sets to only those belonging to templates owned by the user
        user = self.request.user
        return TemplateSet.objects.filter(
            exercise__workout_template__user=user
        )

    def perform_create(self, serializer):
        # Ensure the exercise belongs to the user's template before creation
        exercise = serializer.validated_data.get('exercise')
        if exercise.workout_template.user != self.request.user:
            raise PermissionDenied("You do not have permission to add sets to this exercise.")
        serializer.save()

class TemplateExerciseViewSet(viewsets.ModelViewSet):
    queryset = TemplateExercise.objects.all()
    serializer_class = TemplateExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Still filter for list and other operations
        return TemplateExercise.objects.filter(workout_template__user=self.request.user)

    def get_object(self):
        # For detail views like delete/update, fetch the object ignoring user filtering
        obj = get_object_or_404(TemplateExercise.objects.all(), pk=self.kwargs['pk'])
        return obj

    def perform_create(self, serializer):
        workout_template = serializer.validated_data.get('workout_template')
        if workout_template.user != self.request.user:
            raise PermissionDenied("You do not have permission to add exercises to this template.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.validated_data.pop('workout_template', None)
        serializer.save()

    def perform_destroy(self, instance):
        if instance.workout_template.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this exercise.")
        instance.delete()

class TemplateWorkoutViewSet(viewsets.ModelViewSet):
    serializer_class = TemplateWorkoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list':
            # Only show the authenticated user's templates in the list
            return TemplateWorkout.objects.filter(user=self.request.user)
        # For retrieve/update/delete, return all for manual permission check
        return TemplateWorkout.objects.all()

    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user:
            raise PermissionDenied("You do not have permission to access this template.")
        return obj

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.validated_data.pop('user', None)
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this template.")
        instance.delete()
