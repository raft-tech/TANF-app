"""Tests for generic TDP middleware."""
from types import SimpleNamespace

from django.http import HttpResponse
from django.test import RequestFactory

import pytest

from tdpservice import middleware
from tdpservice.request_attribution import RequestAttribution


class CounterSpy:
    """Capture Prometheus counter label calls without using the global registry."""

    def __init__(self):
        self.calls = []

    def labels(self, **labels):
        """Store the labels used for an increment."""
        self.calls.append({"labels": labels, "increments": 0})
        return self

    def inc(self):
        """Record that the counter was incremented."""
        self.calls[-1]["increments"] += 1


class GroupSpy:
    """Minimal groups manager for middleware identity label tests."""

    def __init__(self, group_names):
        self.group_names = group_names

    def values_list(self, *_args, **_kwargs):
        """Return group names like Django's values_list(..., flat=True)."""
        return self.group_names


class UserRelationTrap:
    """Authenticated user double that fails if relation labels are accessed."""

    is_authenticated = True

    @property
    def stt(self):
        """Fail if middleware tries to read the STT relation."""
        raise AssertionError("stt relation should not be touched")

    @property
    def groups(self):
        """Fail if middleware tries to read the groups relation."""
        raise AssertionError("groups relation should not be touched")


@pytest.fixture
def counter_spy(monkeypatch):
    """Patch the request attribution counter with a local spy."""
    spy = CounterSpy()
    monkeypatch.setattr(middleware, "API_REQUESTS_TOTAL", spy)
    return spy


@pytest.fixture
def request_factory():
    """Return a Django request factory."""
    return RequestFactory()


def _tracked_request(request_factory, path="/v1/users/", method="get", **headers):
    """Build a request with a resolved safe view name."""
    request = getattr(request_factory, method)(path, **headers)
    request.resolver_match = SimpleNamespace(view_name="user-list")
    return request


def _call_middleware(request, status_code=200):
    """Run the attribution middleware around a successful response."""
    attribution_middleware = middleware.RequestAttributionMetricsMiddleware(
        lambda _request: HttpResponse(status=status_code)
    )
    return attribution_middleware(request)


def _last_labels(counter_spy):
    """Return labels from the most recent counter increment."""
    assert len(counter_spy.calls) == 1
    assert counter_spy.calls[0]["increments"] == 1
    return counter_spy.calls[0]["labels"]


def _expected_labels(**overrides):
    """Return the default expected metric labels with selected overrides."""
    labels = {
        "source": "unknown",
        "auth_method": "none",
        "client_id": "none",
        "user_stt": "unknown",
        "user_group": "unknown",
        "method": "GET",
        "status_code": "200",
        "view": "user-list",
    }
    labels.update(overrides)
    return labels


def _set_bearer_attribution(request, client_id="tdp-cli"):
    """Attach verified bearer attribution like the DRF authenticator does."""
    request.tdp_attribution = RequestAttribution(
        source="api_client",
        client_id=client_id,
        auth_method="bearer",
    )


def test_request_attribution_uses_verified_bearer_identity_labels(
    counter_spy, request_factory
):
    """Bearer auth labels come from verified attribution, not user ORM relations."""
    request = _tracked_request(
        request_factory,
        HTTP_AUTHORIZATION="Bearer signed-token",
    )
    request.user = UserRelationTrap()
    request.tdp_attribution = RequestAttribution(
        source="api_client",
        client_id="tdp-cli",
        auth_method="bearer",
        user_stt="1",
        user_group="Data Analyst",
    )

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_method="bearer",
        client_id="tdp-cli",
        user_stt="1",
        user_group="Data Analyst",
    )


def test_request_attribution_records_frontend_header(counter_spy, request_factory):
    """Frontend service headers do not identify unauthenticated request source."""
    request = _tracked_request(
        request_factory,
        HTTP_X_SERVICE_NAME="tdp-frontend",
    )

    _call_middleware(request, status_code=204)

    assert _last_labels(counter_spy) == _expected_labels(status_code="204")


def test_request_attribution_records_session_over_frontend_header(
    counter_spy, request_factory
):
    """Authenticated sessions are the browser-session signal, not headers."""
    request = _tracked_request(
        request_factory,
        HTTP_X_SERVICE_NAME="tdp-frontend",
    )
    request.user = SimpleNamespace(is_authenticated=True)
    request.COOKIES["id_token"] = "cookie-token"

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="browser_session",
        auth_method="session",
        user_stt="none",
        user_group="none",
    )


def test_request_attribution_records_verified_bearer_client(
    counter_spy, request_factory
):
    """Verified bearer context wins over the spoofable frontend header."""
    request = _tracked_request(
        request_factory,
        HTTP_AUTHORIZATION="Bearer signed-token",
        HTTP_X_SERVICE_NAME="tdp-frontend",
    )
    _set_bearer_attribution(request)

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_method="bearer",
        client_id="tdp-cli",
    )


def test_request_attribution_records_verified_bearer_context_without_header(
    counter_spy, request_factory
):
    """Verified bearer auth context is enough to identify the API client."""
    request = _tracked_request(request_factory)
    _set_bearer_attribution(request)
    request.user = SimpleNamespace(is_authenticated=True)

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_method="bearer",
        client_id="tdp-cli",
        user_stt="none",
        user_group="none",
    )


def test_request_attribution_keeps_verified_bearer_on_error_response(
    counter_spy, request_factory
):
    """A verified bearer client remains attributed even when the view rejects it."""
    request = _tracked_request(
        request_factory,
        HTTP_AUTHORIZATION="Bearer signed-token",
    )
    _set_bearer_attribution(request)

    _call_middleware(request, status_code=401)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_method="bearer",
        client_id="tdp-cli",
        status_code="401",
    )


def test_request_attribution_records_authorization_meta_fallback(
    counter_spy, request_factory
):
    """Authorization fallback keys still identify API-client attempts."""
    request = _tracked_request(request_factory)
    request.META.pop("HTTP_AUTHORIZATION", None)
    request.META["Authorization"] = "Bearer signed-token"

    _call_middleware(request, status_code=401)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_method="authorization_header",
        client_id="unknown",
        status_code="401",
    )


def test_request_attribution_records_bearer_client_over_session(
    counter_spy, request_factory
):
    """Authorization headers identify API clients even when cookies are present."""
    request = _tracked_request(
        request_factory,
        HTTP_AUTHORIZATION="Bearer signed-token",
        HTTP_COOKIE="id_token=abc123",
    )
    _set_bearer_attribution(request)
    request.user = SimpleNamespace(is_authenticated=True)

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_method="bearer",
        client_id="tdp-cli",
        user_stt="none",
        user_group="none",
    )


def test_request_attribution_records_unknown_bearer_client(
    counter_spy, request_factory
):
    """Bearer attempts without verified client context stay direct but unknown."""
    request = _tracked_request(
        request_factory,
        HTTP_AUTHORIZATION="Bearer invalid-token",
    )

    _call_middleware(request, status_code=401)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_method="authorization_header",
        client_id="unknown",
        status_code="401",
    )


def test_request_attribution_does_not_verify_expired_bearer_token(
    counter_spy, request_factory
):
    """Legacy client id attributes do not prove bearer attribution."""
    request = _tracked_request(
        request_factory,
        HTTP_AUTHORIZATION="Bearer expired-token",
    )
    request._keycloak_client_id = "tdp-cli"

    _call_middleware(request, status_code=401)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_method="authorization_header",
        client_id="unknown",
        status_code="401",
    )


def test_request_attribution_records_missing_source(counter_spy, request_factory):
    """Requests without auth, frontend, or bearer attribution stay unknown."""
    request = _tracked_request(request_factory)

    _call_middleware(request, status_code=403)

    assert _last_labels(counter_spy) == _expected_labels(
        status_code="403",
    )


def test_request_attribution_ignores_unrecognized_service_header(
    counter_spy, request_factory
):
    """Unexpected service-name values do not identify request source."""
    request = _tracked_request(
        request_factory,
        HTTP_X_SERVICE_NAME="postman",
    )

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels()


def test_request_attribution_records_non_bearer_authorization(
    counter_spy, request_factory
):
    """Non-Bearer Authorization headers are categorized without storing them."""
    request = _tracked_request(
        request_factory,
        HTTP_AUTHORIZATION="Token abc123",
    )

    _call_middleware(request, status_code=403)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_method="authorization_header",
        client_id="unknown",
        status_code="403",
    )


def test_request_attribution_records_authenticated_session(
    counter_spy, request_factory
):
    """Authenticated requests without Authorization are browser-session traffic."""
    request = _tracked_request(request_factory)
    request.user = SimpleNamespace(is_authenticated=True)

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="browser_session",
        auth_method="session",
        user_stt="none",
        user_group="none",
    )


def test_request_attribution_records_authenticated_user_identity(
    counter_spy, request_factory
):
    """Authenticated users include DB-backed STT and group labels."""
    request = _tracked_request(request_factory)
    request.user = SimpleNamespace(
        is_authenticated=True,
        stt_id=1,
        stt=SimpleNamespace(name="Alabama"),
        groups=GroupSpy(["Data Analyst"]),
    )

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="browser_session",
        auth_method="session",
        user_stt="Alabama",
        user_group="Data Analyst",
    )


def test_request_attribution_records_admin_group_without_stt(
    counter_spy, request_factory
):
    """Admin sessions are identifiable by group when no STT is assigned."""
    request = _tracked_request(request_factory)
    request.user = SimpleNamespace(
        is_authenticated=True,
        stt_id=None,
        stt=None,
        groups=GroupSpy(["OFA System Admin"]),
    )

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="browser_session",
        auth_method="session",
        user_stt="none",
        user_group="OFA System Admin",
    )


def test_request_attribution_records_first_group(counter_spy, request_factory):
    """Multiple user groups are collapsed to the first returned group label."""
    request = _tracked_request(request_factory)
    request.user = SimpleNamespace(
        is_authenticated=True,
        stt_id=1,
        stt=SimpleNamespace(name="Alabama"),
        groups=GroupSpy(["OFA System Admin", "Data Analyst"]),
    )

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="browser_session",
        auth_method="session",
        user_stt="Alabama",
        user_group="OFA System Admin",
    )


def test_request_attribution_records_auth_cookie(counter_spy, request_factory):
    """Auth cookies without verified authentication do not identify source."""
    request = _tracked_request(request_factory, HTTP_COOKIE="id_token=abc123")
    request.user = SimpleNamespace(is_authenticated=False)

    _call_middleware(request, status_code=401)

    assert _last_labels(counter_spy) == _expected_labels(status_code="401")


def test_request_attribution_records_cors_preflight(counter_spy, request_factory):
    """CORS preflight requests without auth are left unknown."""
    request = _tracked_request(request_factory, method="options")

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(method="OPTIONS")


def test_request_attribution_skips_prometheus_scrape_path(counter_spy, request_factory):
    """Prometheus scrape traffic is not included in API source metrics."""
    request = _tracked_request(request_factory, path="/prometheus/metrics")

    _call_middleware(request)

    assert counter_spy.calls == []


def test_request_attribution_skips_admin_path(counter_spy, request_factory):
    """Django admin traffic is not included in API source metrics."""
    request = _tracked_request(request_factory, path="/admin/users/user/")

    _call_middleware(request)

    assert counter_spy.calls == []
