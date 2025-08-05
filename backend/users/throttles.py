from rest_framework.throttling import SimpleRateThrottle

class LoginThrottle(SimpleRateThrottle):
    scope = 'login'

    def get_cache_key(self, request, view):
        # Use IP address as key
        ip = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ip
        }