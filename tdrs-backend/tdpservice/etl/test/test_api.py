"""Tests for ETL pipeline API endpoints."""

from unittest.mock import patch

import pytest

from tdpservice.data_files.models import DataFile
from tdpservice.etl.models import ETLPipelineRun


@pytest.mark.django_db
def test_pipeline_list_allows_approved_operational_viewers(api_client, digit_team):
    """Approved DIGIT Team users can inspect registered pipelines."""
    api_client.force_authenticate(user=digit_team)

    response = api_client.get("/v1/etl/pipelines/")

    assert response.status_code == 200
    assert response.data[0]["key"] == "statistical_weights"


@pytest.mark.django_db
def test_pipeline_run_create_requires_ofa_system_admin(api_client, digit_team):
    """View-only operational users cannot start ETL runs."""
    api_client.force_authenticate(user=digit_team)

    response = api_client.post(
        "/v1/etl/runs/",
        {
            "pipeline_key": "statistical_weights",
            "parameters": {
                "fiscal_year": 2026,
                "program": DataFile.ProgramType.TANF,
            },
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_pipeline_run_create_enqueues_approved_pipeline(api_client, ofa_system_admin):
    """OFA System Admin users can create approved pipeline runs."""
    api_client.force_authenticate(user=ofa_system_admin)

    with patch("tdpservice.etl.views.enqueue_pipeline_run") as enqueue_pipeline_run:
        response = api_client.post(
            "/v1/etl/runs/",
            {
                "pipeline_key": "statistical_weights",
                "parameters": {
                    "fiscal_year": "2026",
                    "program": DataFile.ProgramType.TANF,
                },
            },
            format="json",
        )

    assert response.status_code == 201
    assert response.data["pipeline_key"] == "statistical_weights"
    assert response.data["parameters"] == {
        "fiscal_year": 2026,
        "program": DataFile.ProgramType.TANF,
    }
    assert response.data["metadata"] == {}
    assert ETLPipelineRun.objects.count() == 1
    enqueue_pipeline_run.assert_called_once()


@pytest.mark.django_db
def test_pipeline_run_create_rejects_program_alias(api_client, ofa_system_admin):
    """Pipeline run creation requires exact DataFile.ProgramType values."""
    api_client.force_authenticate(user=ofa_system_admin)

    response = api_client.post(
        "/v1/etl/runs/",
        {
            "pipeline_key": "statistical_weights",
            "parameters": {"fiscal_year": 2026, "program": "TANF"},
        },
        format="json",
    )

    assert response.status_code == 400
    assert ETLPipelineRun.objects.count() == 0


@pytest.mark.django_db
def test_pipeline_run_create_rejects_active_duplicate(api_client, ofa_system_admin):
    """Only one active run may exist for the same output scope."""
    api_client.force_authenticate(user=ofa_system_admin)
    request_body = {
        "pipeline_key": "statistical_weights",
        "parameters": {"fiscal_year": 2026, "program": DataFile.ProgramType.TANF},
    }

    with patch("tdpservice.etl.views.enqueue_pipeline_run"):
        first_response = api_client.post("/v1/etl/runs/", request_body, format="json")
        second_response = api_client.post("/v1/etl/runs/", request_body, format="json")

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert ETLPipelineRun.objects.count() == 1
