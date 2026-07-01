"""Tests for project middleware."""

from django.http import HttpResponse
from django.test import RequestFactory

from tdpservice.middleware import SessionMiddleware


def _response_with_origin(origin, settings):
    settings.CORS_ORIGIN_ALLOW_ALL = False
    settings.CORS_ALLOWED_ORIGINS = [
        "https://tanfdata.acf.hhs.gov",
        "https://admin.tanfdata.acf.hhs.gov",
    ]
    request = RequestFactory().get("/", HTTP_ORIGIN=origin)
    middleware = SessionMiddleware(lambda request: HttpResponse())

    return middleware.process_response(request, HttpResponse())


def test_session_middleware_allows_configured_frontend_origin(settings):
    """The primary frontend origin should be echoed from CORS settings."""
    response = _response_with_origin("https://tanfdata.acf.hhs.gov", settings)

    assert response["Access-Control-Allow-Origin"] == "https://tanfdata.acf.hhs.gov"
    assert response["Vary"] == "Origin"


def test_session_middleware_allows_configured_admin_origin(settings):
    """The admin frontend origin should be echoed from CORS settings."""
    response = _response_with_origin("https://admin.tanfdata.acf.hhs.gov", settings)

    assert (
        response["Access-Control-Allow-Origin"]
        == "https://admin.tanfdata.acf.hhs.gov"
    )
    assert response["Vary"] == "Origin"


def test_session_middleware_does_not_allow_unconfigured_origin(settings):
    """Unexpected origins should not receive the allow-origin header."""
    response = _response_with_origin("https://unexpected.example", settings)

    assert "Access-Control-Allow-Origin" not in response
