"""Tests for Reports Application."""
import uuid

import pytest
from rest_framework import status

from ..models import ReportFile


# Create your tests here.
@pytest.mark.django_db
def test_create_report_file_entry(api_client, user):
    """Test report file metadata registry."""
    api_client.login(username=user.username, password="test_password")
    data = {
        "original_filename": "report.txt",
        "quarter": "Q1",
        "slug": str(uuid.uuid4()),
        "user": user.id,
        "stt": user.stt.id,
        "year": 2020,
        "section": "Active Case Data",
    }
    response = api_client.post("/v1/reports/", data)
    # assert response.data == {}
    assert response.data["slug"] == str(data["slug"])
    assert response.status_code == status.HTTP_201_CREATED

    assert ReportFile.objects.filter(
        slug=data["slug"],
        year=data["year"],
        section=data["section"],
        version=1,
        user=user,
    ).exists()


@pytest.mark.django_db
def test_report_file_version_increment(api_client, user):
    """Test that report file version numbers increment."""
    api_client.login(username=user.username, password="test_password")
    data1 = {
        "original_filename": "report.txt",
        "quarter": "Q1",
        "slug": str(uuid.uuid4()),
        "user": user.id,
        "stt": user.stt.id,
        "year": 2020,
        "section": "Active Case Data",
    }
    data2 = {
        "original_filename": "report.txt",
        "quarter": "Q1",
        "slug": data1["slug"],
        "user": user.id,
        "stt": user.stt.id,
        "year": 2020,
        "section": "Active Case Data",
    }

    response1 = api_client.post("/v1/reports/", data1)
    response2 = api_client.post("/v1/reports/", data2)

    assert response1.status_code == status.HTTP_201_CREATED
    assert response1.data["slug"] == data1["slug"]

    assert response2.status_code == status.HTTP_201_CREATED
    assert response2.data["slug"] == data2["slug"]

@pytest.mark.django_db
def test_s3_signed_url(api_client, user):
    api_client.login(username=user.username, password="test_password")
    response = api_client.post("/v1/reports/signed_url/", {
        "file_name":"test.txt",
        "file_type":"plain/text",
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {}
    assert response.data['signed_url']

@pytest.mark.django_db
def test_s3_signed_url(api_client, user):
    api_client.login(username=user.username, password="test_password")
    response = api_client.post("/v1/reports/signed_url/", {
        "file_name":"test.txt",
        "file_type":"plain/text",
    })

    assert response.status_code == status.HTTP_200_OK
    # assert response.data == {}
    assert response.data['signed_url']

@pytest.mark.django_db
def test_individual_report_file_retrieval(api_client, user):
    api_client.login(username=user.username, password="test_password")

    data = {
        "original_filename": "report.txt",
        "quarter": "Q1",
        "slug": str(uuid.uuid4()),
        "user": user,
        "stt": user.stt,
        "year": 2020,
        "section": "Active Case Data",
    }

    ReportFile.create_new_version(data)
    assert ReportFile.objects.filter(**data).exists()
    response = api_client.get("/v1/reports/2020/Q1/active_case_data")

    assert data['slug'] == response.data['slug']
