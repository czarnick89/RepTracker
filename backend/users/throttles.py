from rest_framework.throttling import SimpleRateThrottle

class LoginThrottle(SimpleRateThrottle):
    """
    Custom throttle for login attempts to prevent brute-force attacks.

    Uses the client's IP address as the identifier.
    The rate is defined in REST_FRAMEWORK settings under:
        'DEFAULT_THROTTLE_RATES': {
            'login': '5/minute',  # Example: max 5 login attempts per minute per IP
        }
    """
    scope = 'login'

    def get_cache_key(self, request, view):
        """
        Returns a unique cache key for the request based on client IP.

        DRF uses this cache key to track request count within the time window.
        """
        ip = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ip
        }