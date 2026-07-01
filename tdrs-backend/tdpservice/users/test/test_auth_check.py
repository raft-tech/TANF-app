"""Test the authorization check."""

from urllib.parse import parse_qs, urlparse

from django.urls import reverse

import pytest
from rest_framework import status

from ..serializers import UserProfileSerializer


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
    user_authentication = api_client.login(username=deactivated_user.username, password="test_password")
    response = api_client.get(reverse("authorization-check"))

    assert user_authentication is True
    assert response.data["authenticated"] is False


@pytest.mark.django_db
def test_admin_auth_check_allows_ofa_system_admin(api_client, ofa_system_admin):
    """Admin auth_check should authorize OFA System Admin users."""
    api_client.login(username=ofa_system_admin.username, password="test_password")
    response = api_client.get(reverse("admin-authorization-check"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["authenticated"] is True
    assert response.data["authorized"] is True
    assert response.data["csrf"]


@pytest.mark.django_db
def test_admin_auth_check_rejects_non_admin(api_client, user):
    """Admin auth_check should keep Django authoritative for admin authz."""
    api_client.login(username=user.username, password="test_password")
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
