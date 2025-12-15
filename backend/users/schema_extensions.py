"""
OpenAPI schema extensions for drf-spectacular to properly document custom authentication.
"""
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class JWTCookieAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    Extension to handle our custom JWT authentication from cookies.
    This tells drf-spectacular how to document the cookie-based JWT auth.
    """
    target_class = 'users.authentication.JWTAuthenticationFromCookie'
    name = 'jwtCookieAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'access',
            'description': 'JWT access token stored in HttpOnly cookie. '
                          'Obtain by logging in via /api/v1/users/login/. '
                          'The cookie is automatically sent with requests.'
        }
