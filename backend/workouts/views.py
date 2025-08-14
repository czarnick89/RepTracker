# Standard library
from datetime import timezone

# Django imports
from django.conf import settings
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

# Third-party imports
import requests
from decouple import config
from rest_framework import viewsets, permissions, status as s
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from google_auth_oauthlib.flow import Flow

# Local app imports
from .models import (
    Set,
    Exercise,
    Workout,
    TemplateSet,
    TemplateExercise,
    TemplateWorkout,
)
from .serializers import (
    SetSerializer,
    ExerciseSerializer,
    WorkoutSerializer,
    TemplateSetSerializer,
    TemplateExerciseSerializer,
    TemplateWorkoutSerializer,
)
from .google_calendar_utils import get_google_calendar_service
from .throttles import ExerciseInfoThrottle

User = get_user_model()

# ------------------------------
# Proxy views for external exerciseDB API
# ------------------------------
class ExerciseByNameProxy(APIView):
    """
    Proxies requests to the ExerciseDB API to fetch exercise data by name.
    Applies rate limiting with ExerciseInfoThrottle.
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ExerciseInfoThrottle]

    def get(self, request):
        name = request.query_params.get("name")
        if not name:
            return Response({"detail": "Missing 'name' parameter"}, status=s.HTTP_400_BAD_REQUEST)
        
        url = f"{settings.EXERCISE_DB_BASE_URL}/exercises/name/{name}"
        headers = {
            "X-RapidAPI-Key": config("RAPIDAPI_KEY"),
            "X-RapidAPI-Host": settings.EXERCISE_DB_HOST,
        }
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            return Response({"detail": "Failed to fetch exercise from external API"}, status=resp.status_code)
        return Response(resp.json())

class ExerciseGifProxy(APIView):
    """
    Proxies requests to ExerciseDB to fetch exercise GIFs/images.
    Applies rate limiting with ExerciseInfoThrottle.
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ExerciseInfoThrottle] 

    def get(self, request):
        exercise_db_id = request.query_params.get("exerciseId")
        resolution = request.query_params.get("resolution", "180")
        if not exercise_db_id:
            return HttpResponse("Missing 'exerciseId' parameter", status=400)
        
        url = f"{settings.EXERCISE_DB_BASE_URL}/image"
        params = {"exerciseId": exercise_db_id, "resolution": resolution}
        headers = {
            "X-RapidAPI-Key": config("RAPIDAPI_KEY"),
            "X-RapidAPI-Host": settings.EXERCISE_DB_HOST,
        }
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            return HttpResponse("Image not found", status=resp.status_code)
        return HttpResponse(resp.content, content_type=resp.headers.get("Content-Type"))

# ------------------------------
# CRUD viewsets for workout app
# ------------------------------
class SetViewSet(viewsets.ModelViewSet):
    """
    Standard CRUD for workout sets.
    Filters sets by exercises belonging to the authenticated user.
    """
    queryset = Set.objects.all() # Required for DRF but overwritten below otherwise any user could CRUD by id
    serializer_class = SetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only manipulate sets owned by authenticated user
        return Set.objects.filter(exercise__workout__user=self.request.user)

class ExerciseViewSet(viewsets.ModelViewSet):
    """
    Standard CRUD for exercises.
    Only returns exercises belonging to the authenticated user.
    """
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Exercise.objects.filter(workout__user=self.request.user)

class WorkoutViewSet(viewsets.ModelViewSet):
    """
    Standard CRUD for workouts.
    Includes:
    - get_queryset with prefetch to reduce DB queries for exercises & sets
    - perform_create to automatically assign the current user
    - 'recent' action to fetch paginated list of recent workouts
    """
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return workouts belonging to current user, newest first
        # Prefetch exercises and their sets for performance
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
        """
        Return a paginated list of the user's workouts.
        Query params:
        - offset: how many workouts to skip (default 0)
        - limit: number of workouts to return (default 10)
        """
        try:
            offset = int(request.query_params.get('offset', 0))
            limit = int(request.query_params.get('limit', 10))
        except ValueError:
            offset = 0
            limit = 10

        workouts = self.get_queryset()[offset : offset + limit]
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

class GoogleCalendarAuthStart(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Starts the OAuth2 flow for Google Calendar.
        - Builds a Flow object using client config from settings.
        - Requests offline access so a refresh token is returned.
        - Stores state and user ID in session for later verification.
        - Redirects user to Google's authorization URL.
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": settings.GOOGLE_AUTH_URI,
                    "token_uri": settings.GOOGLE_TOKEN_URI,
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                    "scopes": [
                        config('GOOGLE_API_CALENDAR_EVENTS'),
                        config('GOOGLE_API_CALENDAR_READONLY'),
                    ],
                }
            },
            scopes=[
                config('GOOGLE_API_CALENDAR_EVENTS'),
                config('GOOGLE_API_CALENDAR_READONLY'),
            ],
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
        )
        # Generates the auth URL and state token
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        # Store OAuth state and user ID in session for verification in callback
        request.session["google_oauth_state"] = state
        request.session["google_oauth_user_id"] = request.user.id
        # Redirect the user to Google's consent page
        return redirect(authorization_url)

class GoogleCalendarOAuth2Callback(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """
        Handles the OAuth2 callback from Google:
        - Retrieves state and user ID from session.
        - Reconstructs the Flow object with same client config and state.
        - Fetches tokens using authorization response from Google.
        - Saves access, refresh tokens and expiry to the user model.
        - Redirects user to the frontend profile page.
        """
        state = request.session.get("google_oauth_state")
        user_id = request.session.get("google_oauth_user_id")
        if not user_id:
            return Response({"detail": "User session not found."}, status=400)

        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)
        
        # Rebuild flow with stored state
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": settings.GOOGLE_AUTH_URI,
                    "token_uri": settings.GOOGLE_TOKEN_URI,
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                    "scopes": [
                        config('GOOGLE_API_CALENDAR_EVENTS'),
                        config('GOOGLE_API_CALENDAR_READONLY'),
                    ],
                }
            },
            scopes=[
                config('GOOGLE_API_CALENDAR_EVENTS'),
                config('GOOGLE_API_CALENDAR_READONLY'),
            ],
            state=state,
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
        )
        # Exchange authorization code for access and refresh tokens
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        credentials = flow.credentials
        # Ensure expiry has timezone info
        expiry = credentials.expiry
        if expiry is not None and expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        # Save tokens and expiry to user
        user.google_access_token = credentials.token
        user.google_refresh_token = credentials.refresh_token
        user.google_token_expiry = expiry
        user.save()

        return redirect(settings.FRONTEND_PROFILE_URL)

class AddWorkoutToCalendar(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Adds a new event to the user's Google Calendar:
        - Uses a helper to get authorized calendar service.
        - Builds the event dict from request data.
        - Inserts the event into the primary calendar.
        """
        service = get_google_calendar_service(request.user)
        if not service:
            return Response({"detail": "Google Calendar authorization required."}, status=401)

        data = request.data
        event = {
            "summary": data.get("summary", "Workout"),
            "location": data.get("location", ""),
            "description": data.get("description", ""),
            "start": {"dateTime": data.get("start_time"), "timeZone": "UTC"},
            "end": {"dateTime": data.get("end_time"), "timeZone": "UTC"},
        }
        created_event = service.events().insert(calendarId="primary", body=event).execute()
        return Response({"detail": "Event created", "event_id": created_event.get("id")})

class GoogleCalendarStatus(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Checks if user has an active Google Calendar connection.
        - Returns JSON with connected=True/False.
        - Sets Cache-Control to prevent caching sensitive info.
        """
        service = get_google_calendar_service(request.user)
        connected = service is not None
        response = Response({"connected": connected})
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        return response

class GoogleCalendarDisconnect(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Revokes user's Google access token and clears token fields.
        - Sends revoke request to Google's revoke endpoint.
        - Nulls out access/refresh/expiry fields in user model.
        """
        user = request.user
        if user.google_access_token:
            try:
                requests.post(
                    settings.GOOGLE_REVOKE_URI,
                    params={"token": user.google_access_token},
                    headers={"content-type": "application/x-www-form-urlencoded"},
                )
            except Exception as e:
                pass

        user.google_access_token = None
        user.google_refresh_token = None
        user.google_token_expiry = None
        user.save()
        return Response({"message": "Google Calendar disconnected"})