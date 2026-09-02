"""Unit tests for AlertManager helper."""

from unittest.mock import MagicMock, patch

import pytest
from django.test import override_settings

from tdpservice.alerts.alertmanager import send_alert


def test_send_alert_success():
    """send_alert sends proper payload to AlertManager API."""
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = send_alert(
            alertname="RequestParamMismatch",
            summary="Test summary",
            description="Test description",
            severity="ERROR",
            extra_labels={"endpoint": "/data_files/"},
            extra_annotations={"details": "extra info"},
        )

        assert result is True
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "http://alertmanager:9093/api/v2/alerts"
        payload = kwargs["json"]
        assert len(payload) == 1
        assert payload[0]["labels"]["alertname"] == "RequestParamMismatch"
        assert payload[0]["labels"]["severity"] == "ERROR"
        assert payload[0]["labels"]["endpoint"] == "/data_files/"
        assert payload[0]["labels"]["service"] == "tdp-backend"
        assert payload[0]["annotations"]["summary"] == "Test summary"
        assert payload[0]["annotations"]["description"] == "Test description"
        assert payload[0]["annotations"]["details"] == "extra info"


@override_settings(ALERTMANAGER_URL="")
def test_send_alert_no_url():
    """send_alert returns False when ALERTMANAGER_URL is not set."""
    with patch("requests.post") as mock_post:
        result = send_alert(
            alertname="RequestParamMismatch",
            summary="Test summary",
            description="Test description",
        )
        assert result is False
        mock_post.assert_not_called()


def test_send_alert_request_exception():
    """send_alert returns False and logs warning when requests.post raises an exception."""
    with patch("requests.post", side_effect=Exception("Connection refused")):
        result = send_alert(
            alertname="RequestParamMismatch",
            summary="Test summary",
            description="Test description",
        )
        assert result is False

