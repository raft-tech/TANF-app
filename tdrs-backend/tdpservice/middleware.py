"""Generic middleware for use across the TDP platform."""
import re

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

FRONTEND_SERVICE_NAME = "tdp-frontend"
UNKNOWN_LABEL = "unknown"
NONE_LABEL = "none"
AUTHORIZATION_HEADER_CLIENT_ID = "authorization_header"
SESSION_COOKIE_CLIENT_ID = "session_cookie"
UNRECOGNIZED_SERVICE_CLIENT_ID = "unrecognized_service"
SAFE_LABEL_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]+$")
SAFE_IDENTITY_LABEL_PATTERN = re.compile(r"^[A-Za-z0-9 ._:/()'&,-]+$")
GROUP_LABEL_PRIORITY = (
    "OFA System Admin",
    "OFA Admin",
    "DIGIT Team",
    "OFA Regional Staff",
    "Data Analyst",
    "Developer",
    "ACF OCIO",
)
SKIPPED_PATH_PREFIXES = (
    "/admin/",
    "/prometheus/",
    "/redocs",
    "/swagger",
)


def _safe_label_value(value):
    """Return a bounded Prometheus label value, or ``unknown``."""
    if not isinstance(value, str):
        return UNKNOWN_LABEL
    if not value or len(value) > 100 or not SAFE_LABEL_PATTERN.match(value):
        return UNKNOWN_LABEL
    return value


def _safe_identity_label_value(value):
    """Return a bounded DB-backed identity label value, preserving spaces."""
    if not isinstance(value, str):
        return UNKNOWN_LABEL

    value = " ".join(value.split())
    if not value or len(value) > 100 or not SAFE_IDENTITY_LABEL_PATTERN.match(value):
        return UNKNOWN_LABEL
    return value


def _is_bearer_request(request):
    """Return whether the request attempted bearer-token authentication."""
    authorization_header = request.META.get("HTTP_AUTHORIZATION", "")
    return authorization_header.lower().startswith("bearer ")


def _is_authenticated_request(request):
    """Return whether Django/DRF resolved an authenticated user."""
    user = getattr(request, "user", None)
    return bool(getattr(user, "is_authenticated", False))


def _has_auth_cookie(request):
    """Return whether the request carried a known auth/session cookie."""
    cookie_names = {
        getattr(settings, "SESSION_COOKIE_NAME", None),
        "id_token",
    }
    return any(name and name in request.COOKIES for name in cookie_names)


def _user_stt_label(request):
    """Return the authenticated user's assigned STT name, if any."""
    if not _is_authenticated_request(request):
        return UNKNOWN_LABEL

    user = request.user
    stt = getattr(user, "stt", None)
    if not getattr(user, "stt_id", None) and stt is None:
        return NONE_LABEL

    return _safe_identity_label_value(getattr(stt, "name", None))


def _user_group_label(request):
    """Return one deterministic authenticated user group label, if any."""
    if not _is_authenticated_request(request):
        return UNKNOWN_LABEL

    groups = getattr(request.user, "groups", None)
    if groups is None:
        return NONE_LABEL

    try:
        group_names = set(groups.values_list("name", flat=True))
    except Exception:
        return UNKNOWN_LABEL

    if not group_names:
        return NONE_LABEL

    for group_name in GROUP_LABEL_PRIORITY:
        if group_name in group_names:
            return _safe_identity_label_value(group_name)

    return _safe_identity_label_value(sorted(group_names)[0])


def _request_source_labels(request):
    """Return source/client/reason labels from backend-observed request context."""
    if _is_bearer_request(request):
        client_id = _safe_label_value(
            getattr(request, "_keycloak_client_id", UNKNOWN_LABEL)
        )
        attribution = (
            "bearer_verified" if client_id != UNKNOWN_LABEL else "bearer_unverified"
        )
        return "api_client", client_id, attribution

    if request.META.get("HTTP_X_SERVICE_NAME") == FRONTEND_SERVICE_NAME:
        return "frontend", FRONTEND_SERVICE_NAME, "frontend_header"

    if request.META.get("HTTP_X_SERVICE_NAME"):
        return (
            "api_client",
            UNRECOGNIZED_SERVICE_CLIENT_ID,
            "unrecognized_service_header",
        )

    if request.META.get("HTTP_AUTHORIZATION"):
        return (
            "api_client",
            AUTHORIZATION_HEADER_CLIENT_ID,
            "non_bearer_authorization",
        )

    if _is_authenticated_request(request):
        return "api_client", SESSION_COOKIE_CLIENT_ID, "authenticated_session"

    if _has_auth_cookie(request):
        return "api_client", SESSION_COOKIE_CLIENT_ID, "auth_cookie_present"

    if request.method.upper() == "OPTIONS":
        return UNKNOWN_LABEL, UNKNOWN_LABEL, "cors_preflight"

    return UNKNOWN_LABEL, UNKNOWN_LABEL, "no_attribution"


def _view_name(request):
    """Return the resolved Django view name, without falling back to raw paths."""
    resolver_match = getattr(request, "resolver_match", None)
    return _safe_label_value(getattr(resolver_match, "view_name", UNKNOWN_LABEL))


def _status_labels(status_code):
    """Return status code and status class labels."""
    try:
        numeric_status_code = int(status_code)
    except (TypeError, ValueError):
        return UNKNOWN_LABEL, UNKNOWN_LABEL

    return str(numeric_status_code), f"{numeric_status_code // 100}xx"


def _path_starts_with(path, prefix):
    """Return whether a request path matches a skipped route prefix."""
    return path == prefix.rstrip("/") or path.startswith(prefix)


def _should_record_request(request):
    """Return whether the route should be included in API attribution metrics."""
    path = getattr(request, "path_info", None) or getattr(request, "path", "")
    if any(_path_starts_with(path, prefix) for prefix in SKIPPED_PATH_PREFIXES):
        return False

    static_url = getattr(settings, "STATIC_URL", None)
    if static_url and path.startswith(static_url):
        return False

    media_url = getattr(settings, "MEDIA_URL", None)
    if media_url and path.startswith(media_url):
        return False

    return True


def _record_request_attribution(request, status_code):
    """Increment the request attribution counter for a completed request."""
    if not _should_record_request(request):
        return

    source, client_id, attribution = _request_source_labels(request)
    status_code_label, status_class = _status_labels(status_code)
    API_REQUESTS_TOTAL.labels(
        source=source,
        client_id=client_id,
        user_stt=_user_stt_label(request),
        user_group=_user_group_label(request),
        attribution=attribution,
        method=_safe_label_value(request.method.upper()),
        status_code=status_code_label,
        status_class=status_class,
        view=_view_name(request),
    ).inc()


class RequestAttributionMetricsMiddleware(object):
    """Emit low-cardinality Prometheus metrics for API request attribution."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Record request attribution after the downstream response is known."""
        try:
            response = self.get_response(request)
        except Exception:
            _record_request_attribution(request, 500)
            raise

        _record_request_attribution(request, response.status_code)
        return response


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
