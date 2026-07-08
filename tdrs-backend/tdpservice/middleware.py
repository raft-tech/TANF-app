"""Generic middleware for use across the TDP platform."""
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils.cache import add_never_cache_headers, patch_vary_headers


class NoCacheMiddleware(object):
    """Disable client caching with a Cache-Control header."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Add appropriate headers to the response before sending it out."""
        response = self.get_response(request)
        add_never_cache_headers(response)
        return response


class SessionMiddleware(SessionMiddleware):
    """Patches the existing session middle ware to garentee the correct settings."""

    @staticmethod
    def _get_allowed_origin(request):
        """Return the request origin when it is allowed by CORS settings."""
        origin = request.headers.get("Origin")
        if not origin:
            return None

        if getattr(settings, "CORS_ORIGIN_ALLOW_ALL", False):
            return origin

        if origin in getattr(settings, "CORS_ALLOWED_ORIGINS", []):
            return origin

        return None

    def process_response(self, request, response):
        """Augment the behavior of SessionMiddleware to ensure CSRF cookies are correct."""
        response = super(SessionMiddleware, self).process_response(request, response)

        allowed_origin = self._get_allowed_origin(request)
        if allowed_origin:
            response["Access-Control-Allow-Origin"] = allowed_origin
            patch_vary_headers(response, ("Origin",))
            response[
                "Access-Control-Allow-Headers"
            ] = "xsrf-token, \
                            X-CSRFToken, \
                            X-XSRF-token, \
                            Cookie, \
                            Set-Cookie, \
                            Content-type"

        if settings.SESSION_COOKIE_NAME in response.cookies:
            response.cookies[settings.SESSION_COOKIE_NAME]["samesite"] = "None"

        if settings.CSRF_COOKIE_NAME in response.cookies:
            response.cookies[settings.CSRF_COOKIE_NAME]["SameSite"] = "None"
            response.cookies[settings.CSRF_COOKIE_NAME]["Secure"] = True
        return response
