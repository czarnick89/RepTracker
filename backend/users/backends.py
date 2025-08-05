from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class CaseInsensitiveEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # We support email login, so username here is email
        if username is None:
            username = kwargs.get('email')
        if username is None or password is None:
            return None
        try:
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            # No user found with that email
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
