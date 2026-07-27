"""Generic middleware for use across the TDP platform."""
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils.cache import add_never_cache_headers

from prometheus_client import Counter

API_REQUESTS_TOTAL = Counter(
    "tdp_api_requests_total",
    "Total Django API requests by backend-observed request source.",
    (
        "source",
        "client_id",
        "user_stt",
        "user_group",
        "attribution",
        "method",
        "status_code",
        "status_class",
        "view",
    ),
)


class RequestAttributionMetricsMiddleware(object):
    """Emit low-cardinality Prometheus metrics for API request attribution."""

    FRONTEND_SERVICE_NAME = "tdp-frontend"
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
        authenticated_user = bool(getattr(user, "is_authenticated", False))
        authorization_header = request.META.get("HTTP_AUTHORIZATION", "")
        bearer_request = authorization_header.lower().startswith("bearer ")
        verified_client_id = getattr(request, "_keycloak_client_id", None)
        has_verified_bearer_client = (
            bearer_request and verified_client_id != self.UNKNOWN_LABEL
        )

        source = self.UNKNOWN_LABEL
        client_id = self.UNKNOWN_LABEL
        attribution = "no_attribution"
        if authorization_header:
            source = "api_client"
            client_id = (
                verified_client_id if has_verified_bearer_client else self.UNKNOWN_LABEL
            )
            attribution = (
                "bearer_verified" if has_verified_bearer_client else "bearer_unverified"
            )
        elif authenticated_user:
            source = "browser_session"
            attribution = "authenticated_session"
        else:
            source = "browser_session"
            attribution = "unauthenticated_session"

        user_stt, user_group = (
            self._authenticated_user_labels(user)
            if authenticated_user
            else (self.UNKNOWN_LABEL, self.UNKNOWN_LABEL)
        )

        try:
            numeric_status_code = int(status_code)
        except (TypeError, ValueError):
            status_code_label = self.UNKNOWN_LABEL
            status_class = self.UNKNOWN_LABEL
        else:
            status_code_label = str(numeric_status_code)
            status_class = f"{numeric_status_code // 100}xx"

        resolver_match = getattr(request, "resolver_match", None)
        API_REQUESTS_TOTAL.labels(
            source=source,
            client_id=client_id,
            user_stt=user_stt,
            user_group=user_group,
            attribution=attribution,
            method=request.method.upper(),
            status_code=status_code_label,
            status_class=status_class,
            view=getattr(resolver_match, "view_name", None),
        ).inc()

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
            group_names = groups.values_list("name", flat=True) if groups else list()
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
