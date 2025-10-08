from django.utils.deprecation import MiddlewareMixin


class CacheControlMiddleware(MiddlewareMixin):
    """
    Ensure appropriate Cache-Control headers are set for responses.

    - For API endpoints (paths starting with /api/) or authenticated requests,
      set: no-store, no-cache, must-revalidate, max-age=0
    - For the SPA index.html (root) set no-cache/no-store to prevent browsers
      from caching the HTML shell while allowing static assets to be cached
      by nginx (configured separately).
    - Do not overwrite Cache-Control if it's already set by the view.
    """

    SENSITIVE_CACHE = "no-store, no-cache, must-revalidate, max-age=0"

    def process_response(self, request, response):
        # If response already sets Cache-Control, leave it alone
        if response.has_header("Cache-Control"):
            return response

        path = request.path or ""

        try:
            user_is_authenticated = bool(getattr(request, "user", None) and request.user.is_authenticated)
        except Exception:
            user_is_authenticated = False

        # API endpoints and authenticated responses should never be cached by browsers
        if path.startswith("/api/") or user_is_authenticated:
            response["Cache-Control"] = self.SENSITIVE_CACHE
            return response

        # For the SPA root/index.html serve a non-cached HTML shell so users always
        # get the latest client bootstrapping HTML (static assets remain cacheable)
        ct = response.get("Content-Type", "")
        if (path == "/" or path.endswith("/index.html")) and "text/html" in ct:
            response["Cache-Control"] = self.SENSITIVE_CACHE

        return response
