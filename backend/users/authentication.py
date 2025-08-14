from rest_framework_simplejwt.authentication import JWTAuthentication

class JWTAuthenticationFromCookie(JWTAuthentication):
    """
    Custom JWT authentication class that reads the access token
    from an HttpOnly cookie instead of the Authorization header.
    """
    def authenticate(self, request):
        raw_token = request.COOKIES.get('access_token')
        if not raw_token:
            return None
        validated_token = self.get_validated_token(raw_token)
        # Return a tuple of (user, token) as expected by DRF authentication
        return self.get_user(validated_token), validated_token
