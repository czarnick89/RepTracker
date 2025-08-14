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
    if not (user.google_access_token and user.google_refresh_token and user.google_token_expiry):
        return None  # No tokens stored

    expiry = user.google_token_expiry

    if expiry is None:
        return None

    if timezone.is_naive(expiry):
        expiry = timezone.make_aware(expiry, dt_timezone.utc)

    expiry = expiry.astimezone(dt_timezone.utc).replace(tzinfo=None)

    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        expiry=expiry,
    )

    # Refresh token if expired
    if creds.expired:
        if creds.refresh_token:
            try:
                creds.refresh(Request())
                user.google_access_token = creds.token
                user.google_token_expiry = creds.expiry
                user.save()
            except Exception:
                user.google_access_token = None
                user.google_refresh_token = None
                user.google_token_expiry = None
                user.save()
                return None
        else:
            user.google_access_token = None
            user.google_refresh_token = None
            user.google_token_expiry = None
            user.save()
            return None

    try:
        service = build("calendar", "v3", credentials=creds)
        # Minimal request to validate token
        service.calendarList().list(maxResults=1).execute()
        return service
    except Exception:
        user.google_access_token = None
        user.google_refresh_token = None
        user.google_token_expiry = None
        user.save()
        return None