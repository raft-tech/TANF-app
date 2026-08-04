"""Tests for React admin form metadata and validation endpoints."""

from importlib import import_module

from django.contrib.auth.models import Group

import pytest
from rest_framework import status


def _login_admin_api_session(api_client, user, settings):
    """Create an admin-scoped API session for the given user."""
    assert api_client.login(username=user.username, password="test_password") is True
    session = api_client.session
    session["session_scope"] = "standard"
    session.save()

    engine = import_module(settings.SESSION_ENGINE)
    standard_session = engine.SessionStore(
        api_client.cookies[settings.SESSION_COOKIE_NAME].value
    )
    admin_session = engine.SessionStore()
    admin_session.update(dict(standard_session.items()))
    admin_session["session_scope"] = "admin"
    admin_session.save()
    api_client.cookies[settings.ADMIN_SESSION_COOKIE_NAME] = admin_session.session_key


def _admin_headers(settings):
    """Return headers required by admin API middleware."""
    settings.ADMIN_API_PROXY_TOKEN = "test-admin-proxy-token"
    return {"HTTP_X_ADMIN_PROXY_TOKEN": settings.ADMIN_API_PROXY_TOKEN}


def _admin_form_payload(user):
    """Return a complete payload for the constrained user admin form."""
    return {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "account_approval_status": user.account_approval_status,
        "groups": [str(pk) for pk in user.groups.values_list("id", flat=True)],
        "stt": str(user.stt_id) if user.stt_id else "",
        "regions": [str(pk) for pk in user.regions.values_list("id", flat=True)],
    }


@pytest.mark.django_db
def test_user_admin_form_metadata_endpoint(
    api_client, settings, ofa_system_admin, data_analyst
):
    """Return Django-derived metadata for the user admin workflow."""
    _login_admin_api_session(api_client, ofa_system_admin, settings)

    response = api_client.get(
        f"/admin-api/v1/users/{data_analyst.pk}/admin-form-metadata/",
        **_admin_headers(settings),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["workflow"] == "users.user.change"
    assert response.data["submit_url"] == f"/users/{data_analyst.pk}/admin-form/"

    fields = {field["name"]: field for field in response.data["fields"]}
    assert set(fields) == {
        "username",
        "first_name",
        "last_name",
        "account_approval_status",
        "groups",
        "stt",
        "regions",
    }
    assert fields["username"]["required"] is True
    assert fields["username"]["type"] == "text"
    assert fields["username"]["constraints"]["max_length"] == 150
    assert fields["account_approval_status"]["type"] == "select"
    assert fields["account_approval_status"]["initial"] == "Approved"
    assert {"value": "Approved", "label": "Approved"} in fields[
        "account_approval_status"
    ]["choices"]
    assert fields["groups"]["type"] == "multiselect"
    assert fields["groups"]["initial"] == [
        str(data_analyst.groups.values_list("id", flat=True).get())
    ]
    assert fields["stt"]["initial"] == str(data_analyst.stt_id)


@pytest.mark.django_db
def test_user_admin_form_mutation_saves_valid_form(
    api_client, settings, ofa_system_admin, data_analyst
):
    """Save a valid user admin form through authoritative Django validation."""
    _login_admin_api_session(api_client, ofa_system_admin, settings)
    payload = _admin_form_payload(data_analyst)
    payload["first_name"] = "Updated"

    response = api_client.patch(
        f"/admin-api/v1/users/{data_analyst.pk}/admin-form/",
        payload,
        format="json",
        **_admin_headers(settings),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["ok"] is True
    data_analyst.refresh_from_db()
    assert data_analyst.first_name == "Updated"
    assert response.data["metadata"]["object"]["id"] == str(data_analyst.pk)


@pytest.mark.django_db
def test_user_admin_form_mutation_returns_normalized_field_errors(
    api_client, settings, ofa_system_admin, data_analyst
):
    """Return field errors from the Django form in a normalized shape."""
    _login_admin_api_session(api_client, ofa_system_admin, settings)
    payload = _admin_form_payload(data_analyst)
    payload["groups"] = [
        str(data_analyst.groups.values_list("id", flat=True).get()),
        str(Group.objects.get(name="OFA Admin").id),
    ]

    response = api_client.patch(
        f"/admin-api/v1/users/{data_analyst.pk}/admin-form/",
        payload,
        format="json",
        **_admin_headers(settings),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["ok"] is False
    assert response.data["errors"]["field_errors"] == {
        "groups": ["User should not have multiple groups"]
    }
    assert response.data["errors"]["non_field_errors"] == []


@pytest.mark.django_db
def test_user_admin_form_mutation_returns_normalized_non_field_errors(
    api_client, settings, ofa_system_admin, data_analyst
):
    """Return non-field errors from the Django form in a normalized shape."""
    _login_admin_api_session(api_client, ofa_system_admin, settings)
    payload = _admin_form_payload(data_analyst)
    payload["groups"] = [str(Group.objects.get(name="OFA Regional Staff").id)]
    payload["stt"] = ""
    payload["regions"] = []

    response = api_client.patch(
        f"/admin-api/v1/users/{data_analyst.pk}/admin-form/",
        payload,
        format="json",
        **_admin_headers(settings),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["ok"] is False
    assert response.data["errors"]["field_errors"] == {}
    assert response.data["errors"]["non_field_errors"] == [
        "Users in regional roles must have at least one region or location assigned."
    ]
