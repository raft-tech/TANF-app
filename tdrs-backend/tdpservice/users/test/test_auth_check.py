"""Test the authorization check."""

from importlib import import_module
from urllib.parse import parse_qs, urlparse

from django.urls import reverse

import pytest
from rest_framework import status

from ..serializers import UserProfileSerializer


def _copy_standard_session_to_admin_cookie(api_client, settings):
    """Use the current signed test session as an admin-scoped session."""
    api_client.cookies[settings.ADMIN_SESSION_COOKIE_NAME] = api_client.cookies[
        settings.SESSION_COOKIE_NAME
    ].value


def _client_session_from_cookie(api_client, cookie_name, settings):
    """Return a session store loaded from the named test client cookie."""
    engine = import_module(settings.SESSION_ENGINE)
    return engine.SessionStore(api_client.cookies[cookie_name].value)


@pytest.mark.django_db
def test_auth_check_endpoint_with_no_user(api_client):
    """If there is no user auth_check should return 200 with unauthorized message."""
    response = api_client.get(reverse("authorization-check"))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["authenticated"] is False


@pytest.mark.django_db
def test_auth_check_endpoint_with_authenticated_user(api_client, user):
    """If user is authenticated auth_check should response status OK."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(reverse("authorization-check"))
    assert response.status_code == status.HTTP_200_OK
    assert user.is_authenticated is True
    assert response.data["authenticated"] is True
    assert response.data["user"]["first_name"] == user.first_name
    assert response.data["user"]["last_name"] == user.last_name
    assert response.data["user"]["email"] == user.username
    assert response.data["user"]["roles"] == []


@pytest.mark.django_db
def test_auth_check_endpoint_with_bad_user(api_client):
    """If the user doesn't exist, auth_check should not authenticate."""
    api_client.login(username="nonexistent", password="test_password")
    response = api_client.get(reverse("authorization-check"))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["authenticated"] is False


@pytest.mark.django_db
def test_auth_check_endpoint_with_unauthorized_email(api_client):
    """If the user has an email address not in the system it should not authenticate."""
    api_client.login(username="bademail@example.com", password="test_password")
    response = api_client.get(reverse("authorization-check"))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["authenticated"] is False


@pytest.mark.django_db
def test_auth_check_returns_authenticated(api_client, user):
    """If user is authenticated auth_check should return authenticated true."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(reverse("authorization-check"))
    assert user.is_authenticated is True
    assert response.data["authenticated"] is True


@pytest.mark.django_db
def test_auth_check_returns_user_email(api_client, user):
    """If user is authenticated auth_check should return user data."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(reverse("authorization-check"))
    assert response.data["user"]["email"] == user.username


@pytest.mark.django_db
def test_auth_check_returns_user_stt(api_client, user):
    """If user is authenticated auth_check should return user data."""
    api_client.login(username=user.username, password="test_password")
    serializer = UserProfileSerializer(user)
    response = api_client.get(reverse("authorization-check"))
    assert response.data["user"]["stt"] == serializer.data["stt"]


@pytest.mark.django_db
def test_auth_check_deactivated_user(api_client, deactivated_user):
    """If user is deactivated, return a response indicating the user is inactive."""
    user_authentication = api_client.login(
        username=deactivated_user.username, password="test_password"
    )
    response = api_client.get(reverse("authorization-check"))

    assert user_authentication is True
    assert response.data["authenticated"] is False


@pytest.mark.django_db
def test_standard_session_authenticates_frontend_but_not_admin(
    api_client, ofa_system_admin
):
    """A regular TDP session should not authenticate the admin frontend."""
    api_client.login(username=ofa_system_admin.username, password="test_password")
    frontend_response = api_client.get(reverse("authorization-check"))
    admin_response = api_client.get(reverse("admin-authorization-check"))

    assert frontend_response.status_code == status.HTTP_200_OK
    assert frontend_response.data["authenticated"] is True
    assert frontend_response.data["user"]["email"] == ofa_system_admin.username
    assert admin_response.status_code == status.HTTP_200_OK
    assert admin_response.data["authenticated"] is False


@pytest.mark.django_db
def test_admin_session_authenticates_admin_but_not_frontend(
    api_client, ofa_system_admin, settings
):
    """An admin session should not authenticate the regular TDP frontend."""
    api_client.login(username=ofa_system_admin.username, password="test_password")
    _copy_standard_session_to_admin_cookie(api_client, settings)
    del api_client.cookies[settings.SESSION_COOKIE_NAME]

    admin_response = api_client.get(reverse("admin-authorization-check"))
    frontend_response = api_client.get(reverse("authorization-check"))

    assert admin_response.status_code == status.HTTP_200_OK
    assert admin_response.data["authenticated"] is True
    assert admin_response.data["authorized"] is True
    assert frontend_response.status_code == status.HTTP_200_OK
    assert frontend_response.data["authenticated"] is False


@pytest.mark.django_db
def test_forged_service_header_does_not_use_admin_session(
    api_client, ofa_system_admin, settings
):
    """A regular API request cannot opt into the admin session by header."""
    api_client.login(username=ofa_system_admin.username, password="test_password")
    _copy_standard_session_to_admin_cookie(api_client, settings)
    del api_client.cookies[settings.SESSION_COOKIE_NAME]

    response = api_client.get(
        reverse("authorization-check"), HTTP_X_SERVICE_NAME="tdp-admin"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["authenticated"] is False


@pytest.mark.django_db
def test_admin_api_path_uses_admin_session(api_client, ofa_system_admin, settings):
    """Admin API traffic should use the admin session on the backend path."""
    settings.ADMIN_API_PROXY_TOKEN = "server-only-token"
    api_client.login(username=ofa_system_admin.username, password="test_password")
    _copy_standard_session_to_admin_cookie(api_client, settings)
    del api_client.cookies[settings.SESSION_COOKIE_NAME]

    response = api_client.get(
        "/admin-api/v1/auth_check", HTTP_X_ADMIN_PROXY_TOKEN="server-only-token"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["authenticated"] is True
    assert response.data["user"]["email"] == ofa_system_admin.username


@pytest.mark.django_db
def test_admin_api_path_rejects_missing_proxy_token(
    api_client, ofa_system_admin, settings
):
    """Admin API traffic should not be directly browser-callable."""
    settings.ADMIN_API_PROXY_TOKEN = "server-only-token"
    api_client.login(username=ofa_system_admin.username, password="test_password")
    _copy_standard_session_to_admin_cookie(api_client, settings)
    del api_client.cookies[settings.SESSION_COOKIE_NAME]

    response = api_client.get("/admin-api/v1/auth_check")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_api_path_rejects_unauthenticated_session(api_client, settings):
    """Admin API traffic should require an authenticated admin session."""
    settings.ADMIN_API_PROXY_TOKEN = "server-only-token"

    response = api_client.get(
        "/admin-api/v1/auth_check", HTTP_X_ADMIN_PROXY_TOKEN="server-only-token"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "authenticated": False,
        "detail": "Admin authentication is required.",
    }


@pytest.mark.django_db
def test_admin_api_path_rejects_non_admin_session(api_client, user, settings):
    """Admin API traffic should require OFA System Admin authorization in Django."""
    settings.ADMIN_API_PROXY_TOKEN = "server-only-token"
    api_client.login(username=user.username, password="test_password")
    _copy_standard_session_to_admin_cookie(api_client, settings)
    del api_client.cookies[settings.SESSION_COOKIE_NAME]

    response = api_client.get(
        "/admin-api/v1/auth_check", HTTP_X_ADMIN_PROXY_TOKEN="server-only-token"
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "authenticated": True,
        "authorized": False,
        "detail": "User is not authorized for the admin console.",
    }


@pytest.mark.django_db
def test_admin_auth_check_allows_ofa_system_admin(
    api_client, ofa_system_admin, settings
):
    """Admin auth_check should authorize OFA System Admin users."""
    api_client.login(username=ofa_system_admin.username, password="test_password")
    _copy_standard_session_to_admin_cookie(api_client, settings)
    response = api_client.get(reverse("admin-authorization-check"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["authenticated"] is True
    assert response.data["authorized"] is True
    assert response.data["csrf"]


@pytest.mark.django_db
def test_admin_auth_check_rejects_non_admin(api_client, user, settings):
    """Admin auth_check should keep Django authoritative for admin authz."""
    api_client.login(username=user.username, password="test_password")
    _copy_standard_session_to_admin_cookie(api_client, settings)
    response = api_client.get(reverse("admin-authorization-check"))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["authenticated"] is True
    assert response.data["authorized"] is False


@pytest.mark.django_db
def test_admin_login_uses_admin_keycloak_client(api_client, settings):
    """Admin login should initialize OIDC with the dedicated admin client."""
    settings.KEYCLOAK_TDP_ADMIN_CLIENT_ID = "tdp-admin"
    response = api_client.get(reverse("admin-login-ams"))

    assert response.status_code == status.HTTP_302_FOUND
    query_params = parse_qs(urlparse(response["Location"]).query)
    assert query_params["client_id"] == ["tdp-admin"]
    assert query_params["kc_idp_hint"] == ["ams"]
    assert "/admin-auth/oidc/callback/" in query_params["redirect_uri"][0]
    state = query_params["state"][0]
    session = _client_session_from_cookie(
        api_client, settings.ADMIN_SESSION_COOKIE_NAME, settings
    )
    assert "oidc_client" not in session
    assert session["oidc_clients"][state] == "tdp-admin"


@pytest.mark.django_db
def test_standard_login_clears_legacy_admin_client_marker(api_client):
    """Standard login should not inherit a stale unscoped admin client marker."""
    session = api_client.session
    session["oidc_client"] = "tdp-admin"
    session.save()

    response = api_client.get(reverse("v2-login-ams"))

    assert response.status_code == status.HTTP_302_FOUND
    query_params = parse_qs(urlparse(response["Location"]).query)
    assert query_params["client_id"] != ["tdp-admin"]
    assert "oidc_client" not in api_client.session
