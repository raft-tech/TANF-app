"""Core API tests."""
import uuid

import pytest
from rest_framework import status


@pytest.mark.django_db
def test_write_logs(api_client, ofa_admin):
    """Test endpoint consumption of arbitrary JSON to be logged."""
    user = ofa_admin
    api_client.login(username=user.username, password="test_password")
    data = {
        "original_filename": "report.txt",
        "quarter": "Q1",
        "slug": uuid.uuid4(),
        "user": user.id,
        "stt": user.stt.id,
        "year": 2020,
        "section": "Active Case Data",
        "file_version": "0.0.1",
        "timestamp": "2021-04-26T18:32:43.330Z",
        "type": "error",
        "message": "Something strange happened",
    }
    response = api_client.post("/v1/logs/", data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == 'Success'


@pytest.mark.django_db
def test_log_output(api_client, ofa_admin, caplog):
    """Test endpoint's writing of logs to the output."""
    user = ofa_admin
    api_client.login(username=user.username, password="test_password")
    data = {
        "original_filename": "report.txt",
        "quarter": "Q1",
        "slug": uuid.uuid4(),
        "user": user.id,
        "stt": user.stt.id,
        "year": 2020,
        "section": "Active Case Data",
        "file_version": "0.0.1",
        "timestamp": "2021-04-26T18:32:43.330Z",
        "type": "alert",
        "message": "User submitted files",
    }

    api_client.post("/v1/logs/", data)

    assert "User submitted files" in caplog.text
