"""Tests for RequestParamMismatchMiddleware."""

import json
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import RequestFactory
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart

import pytest

from tdpservice.core.models import BaseLog
from tdpservice.param_mismatch_middleware import RequestParamMismatchMiddleware
from tdpservice.users.test.factories import UserFactory


@pytest.fixture
def request_factory():
    """Return Django RequestFactory."""
    return RequestFactory()


@pytest.fixture
def dummy_response():
    """Return dummy get_response callback."""
    return lambda req: HttpResponse("OK", status=200)


@pytest.mark.django_db
def test_get_request_ignored(request_factory, dummy_response):
    """GET requests are ignored and not inspected for parameter mismatches."""
    middleware = RequestParamMismatchMiddleware(dummy_response)
    request = request_factory.get("/data_files/?stt=1")
    request.user = AnonymousUser()

    with patch("tdpservice.param_mismatch_middleware.send_alert") as mock_alert:
        response = middleware(request)

    assert response.status_code == 200
    assert BaseLog.objects.filter(event_type="request_param_mismatch").count() == 0
    mock_alert.assert_not_called()


@pytest.mark.django_db
def test_post_matching_params(request_factory, dummy_response):
    """POST request with identical query and body params does not log or alert."""
    middleware = RequestParamMismatchMiddleware(dummy_response)
    request = request_factory.post("/data_files/?stt=5&year=2024", data={"stt": "5", "year": "2024"})
    request.user = AnonymousUser()

    with patch("tdpservice.param_mismatch_middleware.send_alert") as mock_alert:
        response = middleware(request)

    assert response.status_code == 200
    assert BaseLog.objects.filter(event_type="request_param_mismatch").count() == 0
    mock_alert.assert_not_called()


@pytest.mark.django_db
def test_post_non_upload_mismatch(request_factory, dummy_response):
    """Non-upload POST with mismatch logs to BaseLog but does not send alert."""
    middleware = RequestParamMismatchMiddleware(dummy_response)
    request = request_factory.post("/api/v1/users/?role=admin", data={"role": "analyst"})
    request.user = AnonymousUser()

    with patch("tdpservice.param_mismatch_middleware.send_alert") as mock_alert:
        response = middleware(request)

    assert response.status_code == 200
    logs = BaseLog.objects.filter(event_type="request_param_mismatch")
    assert logs.count() == 1
    log = logs.first()
    assert log.metadata["mismatches"] == {"role": {"query": "admin", "body": "analyst"}}
    assert log.metadata["is_file_upload"] is False
    mock_alert.assert_not_called()


@pytest.mark.django_db
def test_post_file_upload_mismatch_alerts(request_factory, dummy_response):
    """File upload POST with parameter mismatch logs to BaseLog and sends AlertManager alert."""
    middleware = RequestParamMismatchMiddleware(dummy_response)
    dummy_file = SimpleUploadedFile("test.txt", b"dummy content", content_type="text/plain")
    request = request_factory.post(
        "/data_files/?stt=1",
        data={"stt": "2", "file": dummy_file},
    )
    request.user = AnonymousUser()

    with patch("tdpservice.param_mismatch_middleware.send_alert") as mock_alert:
        response = middleware(request)

    assert response.status_code == 200
    logs = BaseLog.objects.filter(event_type="request_param_mismatch")
    assert logs.count() == 1
    log = logs.first()
    assert log.metadata["mismatches"] == {"stt": {"query": "1", "body": "2"}}
    assert log.metadata["is_file_upload"] is True

    mock_alert.assert_called_once()
    alert_args, alert_kwargs = mock_alert.call_args
    assert alert_kwargs["alertname"] == "RequestParamMismatch"
    assert alert_kwargs["severity"] == "ERROR"
    assert alert_kwargs["extra_labels"]["mismatch_type"] == "file_upload"


@pytest.mark.django_db
def test_put_json_mismatch(request_factory, dummy_response):
    """PUT request with JSON body mismatch logs to BaseLog."""
    middleware = RequestParamMismatchMiddleware(dummy_response)
    payload = json.dumps({"stt": 10, "name": "foo"})
    request = request_factory.put(
        "/api/v1/settings/?stt=20",
        data=payload,
        content_type="application/json",
    )
    request.user = AnonymousUser()

    with patch("tdpservice.param_mismatch_middleware.send_alert") as mock_alert:
        response = middleware(request)

    assert response.status_code == 200
    logs = BaseLog.objects.filter(event_type="request_param_mismatch")
    assert logs.count() == 1
    log = logs.first()
    assert log.metadata["mismatches"] == {"stt": {"query": "20", "body": "10"}}
    mock_alert.assert_not_called()


@pytest.mark.django_db
def test_put_urlencoded_mismatch(request_factory, dummy_response):
    """PUT request with URL-encoded form body detects mismatch and logs to BaseLog."""
    middleware = RequestParamMismatchMiddleware(dummy_response)
    request = request_factory.put(
        "/api/v1/users/?role=admin&section=A",
        data="role=analyst&section=A",
        content_type="application/x-www-form-urlencoded",
    )
    request.user = AnonymousUser()

    with patch("tdpservice.param_mismatch_middleware.send_alert") as mock_alert:
        response = middleware(request)

    assert response.status_code == 200
    logs = BaseLog.objects.filter(event_type="request_param_mismatch")
    assert logs.count() == 1
    log = logs.first()
    assert log.metadata["mismatches"] == {"role": {"query": "admin", "body": "analyst"}}
    assert log.metadata["is_file_upload"] is False
    mock_alert.assert_not_called()


@pytest.mark.django_db
def test_patch_urlencoded_mismatch(request_factory, dummy_response):
    """PATCH request with URL-encoded form body detects mismatch and logs to BaseLog."""
    middleware = RequestParamMismatchMiddleware(dummy_response)
    request = request_factory.patch(
        "/api/v1/users/?role=admin",
        data="role=manager",
        content_type="application/x-www-form-urlencoded",
    )
    request.user = AnonymousUser()

    with patch("tdpservice.param_mismatch_middleware.send_alert") as mock_alert:
        response = middleware(request)

    assert response.status_code == 200
    logs = BaseLog.objects.filter(event_type="request_param_mismatch")
    assert logs.count() == 1
    log = logs.first()
    assert log.metadata["mismatches"] == {"role": {"query": "admin", "body": "manager"}}
    mock_alert.assert_not_called()


@pytest.mark.django_db
def test_put_multipart_mismatch(request_factory, dummy_response):
    """PUT request with multipart/form-data body detects mismatch and alerts for file uploads."""
    middleware = RequestParamMismatchMiddleware(dummy_response)
    dummy_file = SimpleUploadedFile("test.txt", b"dummy content", content_type="text/plain")
    data = encode_multipart(BOUNDARY, {"stt": "2", "file": dummy_file})
    request = request_factory.put(
        "/data_files/?stt=1",
        data=data,
        content_type=MULTIPART_CONTENT,
    )
    request.user = AnonymousUser()

    with patch("tdpservice.param_mismatch_middleware.send_alert") as mock_alert:
        response = middleware(request)

    assert response.status_code == 200
    logs = BaseLog.objects.filter(event_type="request_param_mismatch")
    assert logs.count() == 1
    log = logs.first()
    assert log.metadata["mismatches"] == {"stt": {"query": "1", "body": "2"}}
    assert log.metadata["is_file_upload"] is True
    mock_alert.assert_called_once()


@pytest.mark.django_db
def test_patch_multipart_mismatch(request_factory, dummy_response):
    """PATCH request with multipart/form-data body detects mismatch."""
    middleware = RequestParamMismatchMiddleware(dummy_response)
    data = encode_multipart(BOUNDARY, {"stt": "99", "name": "updated"})
    request = request_factory.patch(
        "/api/v1/settings/?stt=100",
        data=data,
        content_type=MULTIPART_CONTENT,
    )
    request.user = AnonymousUser()

    with patch("tdpservice.param_mismatch_middleware.send_alert") as mock_alert:
        response = middleware(request)

    assert response.status_code == 200
    logs = BaseLog.objects.filter(event_type="request_param_mismatch")
    assert logs.count() == 1
    log = logs.first()
    assert log.metadata["mismatches"] == {"stt": {"query": "100", "body": "99"}}
    assert log.metadata["is_file_upload"] is False
    mock_alert.assert_not_called()


@pytest.mark.django_db
def test_middleware_failsafe_on_exception(request_factory, dummy_response):
    """Middleware handles inspection exceptions gracefully without breaking response."""
    middleware = RequestParamMismatchMiddleware(dummy_response)
    request = request_factory.post("/data_files/?stt=1", data={"stt": "2"})
    request.user = AnonymousUser()

    with patch.object(
        middleware,
        "_find_mismatches",
        side_effect=RuntimeError("Unexpected error during mismatch check"),
    ):
        response = middleware(request)

    assert response.status_code == 200


@pytest.mark.django_db
def test_post_mismatch_records_authenticated_user_from_view(request_factory):
    """Mismatches inspected before view execution record the user authenticated by the view."""
    user = UserFactory()

    def authenticating_response(req):
        req.user = user
        return HttpResponse("OK", status=200)

    middleware = RequestParamMismatchMiddleware(authenticating_response)
    dummy_file = SimpleUploadedFile("test.txt", b"dummy content", content_type="text/plain")
    request = request_factory.post(
        "/data_files/?stt=1",
        data={"stt": "2", "file": dummy_file},
    )
    request.user = AnonymousUser()

    with patch("tdpservice.param_mismatch_middleware.send_alert") as mock_alert:
        response = middleware(request)

    assert response.status_code == 200
    logs = BaseLog.objects.filter(event_type="request_param_mismatch")
    assert logs.count() == 1
    log = logs.first()
    assert str(log.actor_id) == str(user.id)
    assert log.metadata["username"] == user.username
    assert log.metadata["user_id"] == str(user.id)

    mock_alert.assert_called_once()
    _, alert_kwargs = mock_alert.call_args
    assert user.username in alert_kwargs["description"]


@pytest.mark.django_db
def test_middleware_failsafe_on_handle_mismatch_exception(request_factory, dummy_response):
    """Middleware handles mismatch handling exceptions gracefully without breaking response."""
    middleware = RequestParamMismatchMiddleware(dummy_response)
    dummy_file = SimpleUploadedFile("test.txt", b"dummy content", content_type="text/plain")
    request = request_factory.post("/data_files/?stt=1", data={"stt": "2", "file": dummy_file})
    request.user = AnonymousUser()

    with patch.object(
        middleware,
        "_handle_mismatch",
        side_effect=RuntimeError("Unexpected error during mismatch handling"),
    ):
        response = middleware(request)

    assert response.status_code == 200
