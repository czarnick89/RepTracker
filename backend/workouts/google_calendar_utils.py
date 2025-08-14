# Standard library
from datetime import timezone as dt_timezone

# Django imports
from django.conf import settings
from django.utils import timezone

# Third-party / Google API imports
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def get_google_calendar_service(user):
    """
    Returns a Google Calendar service object for a user if valid tokens exist.
    Handles token expiry and automatic refresh.
    
    Returns:
        service (googleapiclient.discovery.Resource) or None
    """
    # If any token or expiry is missing, cannot use Google Calendar
    if not (user.google_access_token and user.google_refresh_token and user.google_token_expiry):
        return None 

    expiry = user.google_token_expiry

    if expiry is None:
        return None
    
    # Ensure expiry has timezone info; Google Credentials expects aware datetime
    if timezone.is_naive(expiry):
        expiry = timezone.make_aware(expiry, dt_timezone.utc)

    # Convert to UTC and remove tzinfo for the Credentials object
    expiry = expiry.astimezone(dt_timezone.utc).replace(tzinfo=None)

    # Create Google Credentials object
    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri=settings.GOOGLE_TOKEN_URI,
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        expiry=expiry,
    )

    # Automatically refresh token if expired
    if creds.expired:
        if creds.refresh_token:
            try:
                creds.refresh(Request()) # Refresh token using Google's Request object
                # Save new token and expiry back to user
                user.google_access_token = creds.token
                user.google_token_expiry = creds.expiry
                user.save()
            except Exception:
                # If refresh fails, clear tokens
                user.google_access_token = None
                user.google_refresh_token = None
                user.google_token_expiry = None
                user.save()
                return None
        else:
            # No refresh token, clear credentials
            user.google_access_token = None
            user.google_refresh_token = None
            user.google_token_expiry = None
            user.save()
            return None

    try:
        # Build the service object for Google Calendar API
        service = build("calendar", "v3", credentials=creds)
        # Minimal request to validate credentials
        service.calendarList().list(maxResults=1).execute()
        return service
    except Exception:
        # If any error occurs (token invalid, revoked, etc.), clear tokens
        user.google_access_token = None
        user.google_refresh_token = None
        user.google_token_expiry = None
        user.save()
        return None