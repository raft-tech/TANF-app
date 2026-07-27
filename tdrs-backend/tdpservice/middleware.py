"""Generic middleware for use across the TDP platform."""
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils.cache import add_never_cache_headers

from prometheus_client import Counter

from tdpservice.request_attribution import (
    REQUEST_ATTRIBUTION_ATTRIBUTE,
    RequestAttribution,
)

API_REQUESTS_TOTAL = Counter(
    "tdp_api_requests_total",
    "Total Django API requests by backend-observed request source.",
    (
        "source",
        "auth_method",
        "client_id",
        "user_stt",
        "user_group",
        "method",
        "status_code",
        "view",
    ),
)


class RequestAttributionMetricsMiddleware(object):
    """Emit low-cardinality Prometheus metrics for API request attribution."""

    UNKNOWN_LABEL = "unknown"
    NONE_LABEL = "none"
    SKIPPED_PATH_PREFIXES = (
        "/admin/",
        "/prometheus/",
        "/redocs",
        "/swagger",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Record request attribution after the downstream response is known."""
        try:
            response = self.get_response(request)
        except Exception:
            self._record_request_attribution(request, 500)
            raise

        self._record_request_attribution(request, response.status_code)
        return response

    def _record_request_attribution(self, request, status_code):
        """Increment the request attribution counter for a completed request."""
        if not self._should_record_request(request):
            return

        user = getattr(request, "user", None)
        user_is_authenticated = bool(getattr(user, "is_authenticated", False))
        attribution = self._request_attribution(request, user_is_authenticated)
        status_code_label = str(status_code)

        user_stt, user_group = (
            self._authenticated_user_labels(user)
            if user_is_authenticated
            else (self.UNKNOWN_LABEL, self.UNKNOWN_LABEL)
        )

        resolver_match = getattr(request, "resolver_match", None)
        API_REQUESTS_TOTAL.labels(
            source=attribution.source,
            auth_method=attribution.auth_method,
            client_id=attribution.client_id,
            user_stt=user_stt,
            user_group=user_group,
            method=request.method.upper(),
            status_code=status_code_label,
            view=getattr(resolver_match, "view_name", None) or self.UNKNOWN_LABEL,
        ).inc()

    def _request_attribution(self, request, user_is_authenticated):
        """Return the attribution context for a request."""
        attribution = getattr(request, REQUEST_ATTRIBUTION_ATTRIBUTE, None)
        if attribution is not None:
            return attribution

        if self._authorization_header(request):
            return RequestAttribution(
                source="api_client",
                client_id=self.UNKNOWN_LABEL,
                auth_method="authorization_header",
            )

        if user_is_authenticated:
            return RequestAttribution(
                source="browser_session",
                auth_method="session",
            )

        return RequestAttribution()

    def _authorization_header(self, request):
        """Return the Authorization header value, if Django exposed one."""
        headers = getattr(request, "headers", None)
        if headers:
            authorization_header = headers.get("Authorization", "")
            if authorization_header:
                return authorization_header

        return (
            request.META.get("HTTP_AUTHORIZATION")
            or request.META.get("Authorization")
            or request.META.get("REDIRECT_HTTP_AUTHORIZATION")
            or ""
        )

    def _should_record_request(self, request):
        """Return whether the route should be included in API attribution metrics."""
        path = getattr(request, "path_info", None) or getattr(request, "path", "")
        if any(
            path == prefix.rstrip("/") or path.startswith(prefix)
            for prefix in self.SKIPPED_PATH_PREFIXES
        ):
            return False

        static_url = getattr(settings, "STATIC_URL", None)
        if static_url and path.startswith(static_url):
            return False

        media_url = getattr(settings, "MEDIA_URL", None)
        if media_url and path.startswith(media_url):
            return False

        return True

    def _authenticated_user_labels(self, user):
        """Return STT and group labels for an authenticated Django user."""
        stt = getattr(user, "stt", None)
        user_stt = (
            self.NONE_LABEL
            if not getattr(user, "stt_id", None) and stt is None
            else getattr(stt, "name", self.NONE_LABEL)
        )

        groups = getattr(user, "groups", None)
        try:
            group_names = groups.values_list("name", flat=True) if groups else []
        except Exception:
            return user_stt, self.UNKNOWN_LABEL

        if not group_names:
            return user_stt, self.NONE_LABEL

        return user_stt, group_names[0]


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

    def process_response(self, request, response):
        """Augment the behavior of SessionMiddleware to ensure CSRF cookies are correct."""
        response = super(SessionMiddleware, self).process_response(request, response)

        response["Access-Control-Allow-Origin"] = "https://tanfdata.acf.hhs.gov"
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
