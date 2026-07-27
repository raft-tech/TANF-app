"""Tests for generic TDP middleware."""
from types import SimpleNamespace

from django.http import HttpResponse
from django.test import RequestFactory

import pytest

from tdpservice import middleware


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
        "auth_state": "unauthenticated",
        "client_id": "unknown",
        "user_stt": "unknown",
        "user_group": "unknown",
        "attribution": "no_attribution",
        "method": "GET",
        "status_code": "200",
        "status_class": "2xx",
        "view": "user-list",
    }
    labels.update(overrides)
    return labels


def test_request_attribution_records_frontend_header(counter_spy, request_factory):
    """Frontend service headers are informational when no auth is available."""
    request = _tracked_request(
        request_factory,
        HTTP_X_SERVICE_NAME="tdp-frontend",
    )

    _call_middleware(request, status_code=204)

    assert _last_labels(counter_spy) == _expected_labels(
        attribution="frontend_header",
        status_code="204",
    )


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
        auth_state="authenticated",
        user_stt="none",
        user_group="none",
        attribution="authenticated_session",
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
    request._keycloak_client_id = "tdp-cli"

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_state="authenticated",
        client_id="tdp-cli",
        attribution="bearer_verified",
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
    request._keycloak_client_id = "tdp-cli"
    request.user = SimpleNamespace(is_authenticated=True)

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="api_client",
        auth_state="authenticated",
        client_id="tdp-cli",
        user_stt="none",
        user_group="none",
        attribution="bearer_verified",
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
        attribution="bearer_unverified",
        status_code="401",
        status_class="4xx",
    )


def test_request_attribution_records_missing_source(counter_spy, request_factory):
    """Requests without auth, frontend, or bearer attribution stay unknown."""
    request = _tracked_request(request_factory)

    _call_middleware(request, status_code=403)

    assert _last_labels(counter_spy) == _expected_labels(
        status_code="403",
        status_class="4xx",
    )


def test_request_attribution_records_unrecognized_service_header(
    counter_spy, request_factory
):
    """Unexpected service-name values are categorized without storing the value."""
    request = _tracked_request(
        request_factory,
        HTTP_X_SERVICE_NAME="postman",
    )

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        attribution="unrecognized_service_header",
    )


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
        attribution="non_bearer_authorization",
        status_code="403",
        status_class="4xx",
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
        auth_state="authenticated",
        user_stt="none",
        user_group="none",
        attribution="authenticated_session",
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
        auth_state="authenticated",
        user_stt="Alabama",
        user_group="Data Analyst",
        attribution="authenticated_session",
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
        groups=GroupSpy(["Data Analyst", "OFA System Admin"]),
    )

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        source="browser_session",
        auth_state="authenticated",
        user_stt="none",
        user_group="OFA System Admin",
        attribution="authenticated_session",
    )


def test_request_attribution_records_auth_cookie(counter_spy, request_factory):
    """Auth cookies without verified authentication stay unknown-source."""
    request = _tracked_request(request_factory, HTTP_COOKIE="id_token=abc123")
    request.user = SimpleNamespace(is_authenticated=False)

    _call_middleware(request, status_code=401)

    assert _last_labels(counter_spy) == _expected_labels(
        attribution="auth_cookie_present",
        status_code="401",
        status_class="4xx",
    )


def test_request_attribution_records_cors_preflight(counter_spy, request_factory):
    """CORS preflight requests are identifiable without using raw headers."""
    request = _tracked_request(request_factory, method="options")

    _call_middleware(request)

    assert _last_labels(counter_spy) == _expected_labels(
        attribution="cors_preflight",
        method="OPTIONS",
    )


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
