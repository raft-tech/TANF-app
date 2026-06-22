"""Tests for Cloud.gov environment-specific settings."""

import importlib
import json
import sys

import pytest


def build_vcap_services(service_basename):
    """Return minimal Cloud.gov service bindings for settings import."""
    return {
        "aws-rds": [
            {
                "instance_name": f"tdp-db-{service_basename}",
                "credentials": {
                    "db_name": "tdp_db",
                    "username": "tdpuser",
                    "password": "password",
                    "host": "database.internal",
                    "port": "5432",
                },
            }
        ],
        "s3": [
            {
                "instance_name": f"tdp-datafiles-{service_basename}",
                "credentials": {
                    "access_key_id": "datafiles-access-key",
                    "secret_access_key": "datafiles-secret-key",
                    "bucket": "datafiles-bucket",
                    "endpoint": "s3.example.gov",
                    "region": "us-gov-west-1",
                },
            },
            {
                "instance_name": f"tdp-staticfiles-{service_basename}",
                "credentials": {
                    "access_key_id": "staticfiles-access-key",
                    "secret_access_key": "staticfiles-secret-key",
                    "bucket": "staticfiles-bucket",
                    "endpoint": "s3.example.gov",
                    "region": "us-gov-west-1",
                },
            },
        ],
        "user-provided": [
            {
                "instance_name": f"tdp-keycloak-{service_basename}",
                "credentials": {
                    "admin_client_id": "tdp-django",
                    "admin_client_secret": "admin-secret",
                    "django_client_id": "tdp-django",
                    "django_client_secret": "django-secret",
                },
            }
        ],
    }


def import_cloudgov_settings(monkeypatch, space_name, app_name):
    """Import CloudGov settings after installing synthetic Cloud.gov env vars."""
    service_basename = space_name.replace("tanf-", "", 1)
    monkeypatch.setenv(
        "VCAP_APPLICATION",
        json.dumps({"space_name": space_name, "name": app_name}),
    )
    monkeypatch.setenv(
        "VCAP_SERVICES",
        json.dumps(build_vcap_services(service_basename)),
    )
    monkeypatch.delenv("KEYCLOAK_SERVER_URL", raising=False)
    monkeypatch.delenv("KEYCLOAK_BROWSER_URL", raising=False)
    monkeypatch.delenv("KEYCLOAK_ISSUER", raising=False)

    sys.modules.pop("tdpservice.settings.cloudgov", None)
    return importlib.import_module("tdpservice.settings.cloudgov")


@pytest.mark.parametrize(
    (
        "space_name",
        "app_name",
        "settings_class_name",
        "expected_server_url",
        "expected_browser_url",
        "expected_hosts",
        "expected_origins",
        "expected_set_audience",
    ),
    [
        (
            "tanf-dev",
            "tdp-backend-raft",
            "Development",
            "http://dev.auth.apps.internal:8080",
            "https://dev.auth.tanfdata.acf.hhs.gov",
            {
                "test.tanfdata.acf.hhs.gov",
                "qasp.tanfdata.acf.hhs.gov",
                "a11y.tanfdata.acf.hhs.gov",
            },
            {
                "https://test.tanfdata.acf.hhs.gov",
                "https://qasp.tanfdata.acf.hhs.gov",
                "https://a11y.tanfdata.acf.hhs.gov",
            },
            "https://test.tanfdata.acf.hhs.gov/v1/security/event-token/",
        ),
        (
            "tanf-staging",
            "tdp-backend-staging",
            "Staging",
            "http://staging.auth.apps.internal:8080",
            "https://staging.auth.tanfdata.acf.hhs.gov",
            {
                "develop.tanfdata.acf.hhs.gov",
                "staging.tanfdata.acf.hhs.gov",
            },
            {
                "https://develop.tanfdata.acf.hhs.gov",
                "https://staging.tanfdata.acf.hhs.gov",
            },
            "https://staging.tanfdata.acf.hhs.gov/v1/security/event-token/",
        ),
        (
            "tanf-prod",
            "tdp-backend-prod",
            "Production",
            "http://auth.apps.internal:8080",
            "https://auth.tanfdata.acf.hhs.gov",
            {"tanfdata.acf.hhs.gov"},
            {"https://tanfdata.acf.hhs.gov"},
            "https://tanfdata.acf.hhs.gov/v1/security/event-token/",
        ),
    ],
)
def test_cloudgov_custom_domain_defaults(
    monkeypatch,
    space_name,
    app_name,
    settings_class_name,
    expected_server_url,
    expected_browser_url,
    expected_hosts,
    expected_origins,
    expected_set_audience,
):
    """Cloud.gov settings should default to canonical TDP and Keycloak domains."""
    cloudgov = import_cloudgov_settings(monkeypatch, space_name, app_name)
    settings_class = getattr(cloudgov, settings_class_name)

    assert settings_class.KEYCLOAK_SERVER_URL == expected_server_url
    assert settings_class.KEYCLOAK_BROWSER_URL == expected_browser_url
    assert settings_class.SESSION_COOKIE_DOMAIN == ".tanfdata.acf.hhs.gov"
    assert expected_hosts.issubset(set(settings_class.ALLOWED_HOSTS))
    assert expected_origins.issubset(set(settings_class.CORS_ALLOWED_ORIGINS))
    assert settings_class.LOGIN_GOV_SET_AUDIENCE == expected_set_audience

    assert ".app.cloud.gov" not in settings_class.ALLOWED_HOSTS
    assert "tdp-frontend-prod.app.cloud.gov" not in settings_class.ALLOWED_HOSTS
    assert "tdp-frontend-staging.acf.hhs.gov" not in settings_class.ALLOWED_HOSTS
    assert "tdp-frontend-develop.acf.hhs.gov" not in settings_class.ALLOWED_HOSTS
    assert all(
        "tdp-frontend-" not in origin for origin in settings_class.CORS_ALLOWED_ORIGINS
    )
