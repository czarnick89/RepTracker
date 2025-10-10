from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseBadRequest
import re


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


class BlockSuspiciousParamsMiddleware(MiddlewareMixin):
    """
    Reject requests that contain suspicious parameter names commonly used in
    Spring4Shell/Payload probes, e.g. keys that start with `class.` or contain
    `module.classLoader`. This is defensive and intended to return a 400 for
    obvious probe attempts targeting Java SOAP/Servlet environments.

    This is a quick mitigation for scanners generating payloads against non-Java
    backends (like this Django app) and will reduce false-positive findings in
    automated scanners.
    """

    SUSPICIOUS_KEY_RE = re.compile(r"(^|\.|\[)(class|module|ClassLoader)\b", re.IGNORECASE)

    def process_request(self, request):
        # Check GET params
        for k in request.GET.keys():
            if self.SUSPICIOUS_KEY_RE.search(k):
                return HttpResponseBadRequest("Bad request")

        # Check POST params (form-encoded) and query string keys
        # For JSON bodies we can check the raw payload string for suspicious tokens
        for k in request.POST.keys():
            if self.SUSPICIOUS_KEY_RE.search(k):
                return HttpResponseBadRequest("Bad request")

        try:
            content_type = request.META.get("CONTENT_TYPE", "")
            if "application/json" in content_type:
                # Peek at the body safely (it may be a bytes-like object)
                body = request.body.decode("utf-8", errors="ignore")
                if "class.module.classLoader" in body or "class.module" in body:
                    return HttpResponseBadRequest("Bad request")
        except Exception:
            # If anything goes wrong reading the body, don't block the request
            # based on body parsing — only block based on param keys above.
            pass

        return None
