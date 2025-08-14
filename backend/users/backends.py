from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class CaseInsensitiveEmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using
    email (case-insensitive) instead of username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # If username is not provided, try to get email from kwargs
        if username is None:
            username = kwargs.get('email')
        # If either username/email or password is missing, fail authentication
        if username is None or password is None:
            return None
        try:
            # Look up user by email case-insensitively
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            # Return None if no matching user is found
            return None
        else:
            # Check password and if user is active
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        # If you made is this far authentication failed
        return None
