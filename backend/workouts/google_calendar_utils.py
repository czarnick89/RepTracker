from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.utils import timezone
from django.conf import settings
from google.auth.transport.requests import Request
import logging
from datetime import timezone as dt_timezone

logger = logging.getLogger(__name__)

def get_google_calendar_service(user):
    if not (user.google_access_token and user.google_refresh_token and user.google_token_expiry):
        return None  # No tokens stored

    expiry = user.google_token_expiry

    if expiry is None:
        return None

    if timezone.is_naive(expiry):
        expiry = timezone.make_aware(expiry, dt_timezone.utc)

    # Convert to UTC timezone to normalize, then make naive by stripping tzinfo
    expiry = expiry.astimezone(dt_timezone.utc).replace(tzinfo=None)

    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        expiry=expiry,  # <-- naive UTC datetime here
    )

    logger.debug(f"Credentials expiry: {creds.expiry} (naive? {timezone.is_naive(creds.expiry)})")

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            user.google_access_token = creds.token
            user.google_token_expiry = creds.expiry
            user.save()
        except Exception as e:
            logger.error(f"Failed to refresh Google token for user {user.id}: {e}")
            return None

    if creds.expired and not creds.refresh_token:
        return None

    service = build('calendar', 'v3', credentials=creds)
    return service
