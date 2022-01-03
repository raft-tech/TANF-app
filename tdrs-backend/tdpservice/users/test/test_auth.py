"""Test the custom authorization class."""
import datetime
import os
import secrets
import time
import uuid

from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from rest_framework import status
from rest_framework.test import APIRequestFactory
import jwt
import pytest

from tdpservice.settings.common import get_required_env_var_setting
from tdpservice.users.api.login import TokenAuthorizationLoginDotGov, TokenAuthorizationAMS
from tdpservice.users.api.logout_redirect_oidc import LogoutRedirectOIDC
from tdpservice.users.api.utils import (
    generate_client_assertion,
    generate_jwt_from_jwks,
    generate_token_endpoint_parameters,
    response_internal,
)
from tdpservice.users.authentication import CustomAuthentication
from tdpservice.users.models import User


class MockRequest:
    """Mock request class."""

    def __init__(self, status_code=status.HTTP_200_OK, data=None):
        self.status_code = status_code
        self.data = data

    def json(self):
        """Return data."""
        return self.data


@pytest.fixture
def patch_login_gov_jwt_key(settings, test_private_key):
    """Override JWT Key setting with the key needed for tests."""
    assert test_private_key is not None, 'Unable to generate test_private_key'
    settings.LOGIN_GOV_JWT_KEY = test_private_key.decode("utf-8")


@pytest.fixture
def patch_ams_jwt_key(settings, test_private_key):
    """Override JWT Key setting with the key needed for tests."""
    assert test_private_key is not None, 'Unable to generate test_private_key'
    settings.AMS_CLIENT_SECRET = test_private_key.decode("utf-8")


@pytest.fixture
def mock_token():
    """Retrieve the mock token to be used for tests."""
    return os.getenv(
        'MOCK_TOKEN',
        'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJiMmQyZDExNS0xZDdlLTQ1N'
        'zktYjlkNi1mOGU4NGY0ZjU2Y2EiLCJpc3MiOiJodHRwczovL2lkcC5pbnQubG9naW4uZ29'
        '2IiwiYWNyIjoiaHR0cDovL2lkbWFuYWdlbWVudC5nb3YvbnMvYXNzdXJhbmNlL2xvYS8xI'
        'iwibm9uY2UiOiJhYWQwYWE5NjljMTU2YjJkZmE2ODVmODg1ZmFjNzA4MyIsImF1ZCI6InV'
        'ybjpnb3Y6Z3NhOm9wZW5pZGNvbm5lY3Q6ZGV2ZWxvcG1lbnQiLCJqdGkiOiJqQzdOblU4Z'
        'E5OVjVsaXNRQm0xanRBIiwiYXRfaGFzaCI6InRsTmJpcXIxTHIyWWNOUkdqendsSWciLCJ'
        'jX2hhc2giOiJoWGpxN2tPcnRRS196YV82dE9OeGN3IiwiZXhwIjoxNDg5Njk0MTk2LCJpY'
        'XQiOjE0ODk2OTQxOTgsIm5iZiI6MTQ4OTY5NDE5OH0.pVbPF-2LJSG1fE9thn27PwmDlNd'
        'lc3mEm7fFxb8ZADdRvYmDMnDPuZ3TGHl0ttK78H8NH7rBpH85LZzRNtCcWjS7QcycXHMn0'
        '0Cuq_Bpbn7NRdf3ktxkBrpqyzIArLezVJJVXn2EeykXMvzlO-fJ7CaDUaJMqkDhKOK6caR'
        'YePBLbZJFl0Ri25bqXugguAYTyX9HACaxMNFtQOwmUCVVr6WYL1AMV5WmaswZtdE8POxYd'
        'hzwj777rkgSg555GoBDZy3MetapbT0csSWqVJ13skWTXBRrOiQQ70wzHAu_3ktBDXNoLx4'
        'kG1fr1BiMEbHjKsHs14X8LCBcIMdt49hIZg'
    )


@pytest.fixture()
def states_factory():
    """Bundle together nonce, state, and code for tests."""
    yield {
        'nonce': "testnonce",
        'state': "teststate",
        'code': secrets.token_hex(32)
    }


@pytest.fixture()
def req_factory(states_factory, mock, api_client):
    """Generate a client request for API usage, part of DRY."""
    states = states_factory
    factory = APIRequestFactory()
    request = factory.get(
        "/v1/login",
        {
            "state": states['state'],
            "code": states['code']
        }
    )
    request.session = api_client.session
    # Add an origin param to test multiple auth handlers.
    yield request


@pytest.mark.django_db
def test_authentication(user):
    """Test authentication method."""
    authenticated_user = CustomAuthentication.authenticate(username=user.username)
    assert authenticated_user.username == user.username


@pytest.mark.django_db
def test_get_user(user):
    """Test get_user method."""
    found_user = CustomAuthentication.get_user(user.pk)
    assert found_user.username == user.username


@pytest.mark.django_db
def test_get_non_user(user):
    """Test that an invalid user does not return a user."""
    test_uuid = uuid.uuid1()
    nonuser = CustomAuthentication.get_user(test_uuid)
    assert nonuser is None


@pytest.mark.django_db
class TestLoginAMS:
    """Associate a set of related tests into a class for shared mock fixtures."""

    mock_configuration = {
        "authorization_endpoint": "http://openid-connect/auth",
        "end_session_endpoint": "http://openid-connect/logout",
        "token_endpoint": "http://openid-connect/token",
        "jwks_uri": "http://openid-connect/certs",
        "issuer": "http://realms/ams",
        "userinfo_endpoint": "http://openid-connect/userinfo"
    }

    @pytest.fixture(autouse=True)
    def mock_ams_configuration(self, requests_mock, settings, mock_token):
        """Mock outgoing requests in various parts of the AMS flow."""
        requests_mock.get(settings.AMS_CONFIGURATION_ENDPOINT, json=TestLoginAMS.mock_configuration)

        jwk = {
            "kty": "EC",
            "crv": "P-256",
            "x": "f83OJ3D2xF1Bg8vub9tLe1gHMzV76e8Tus9uPHvRVEU",
            "y": "x_FEzRu9m36HLN_tue659LNpXW6pCyStikYjKIWI5a0",
            "kid": "Public key used in JWS spec Appendix A.3 example",
        }
        requests_mock.get(TestLoginAMS.mock_configuration["jwks_uri"], json={"keys": [jwk]})

        requests_mock.post(TestLoginAMS.mock_configuration["userinfo_endpoint"],
                           json={"email": "test_existing@example.com"})
        requests_mock.post(TestLoginAMS.mock_configuration["token_endpoint"], json={
            "access_token": "hhJES3wcgjI55jzjBvZpNQ",
            "token_type": "Bearer",
            "expires_in": 3600,
            "id_token": mock_token,
        })

    @pytest.fixture(autouse=True)
    def mock_decode(self, states_factory, mocker):
        """Generate all the mock-up data structs needed for API tests."""
        mock_decode = mocker.patch("tdpservice.users.api.login.jwt.decode")

        mock_decode.return_value = decoded_token(
            "test@example.com",
            states_factory['nonce']
        )

        yield mock_decode

    @pytest.fixture()
    def req_factory(self, states_factory, api_client):
        """Generate a client request for API usage, part of DRY."""
        states = states_factory
        factory = APIRequestFactory()
        request = factory.get(
            "/v1/login",
            {
                "state": states["state"],
                "code": states["code"]
            }
        )
        request.session = api_client.session
        # Add an origin param to test multiple auth handlers.
        yield request

    def test_login_ams_auth(self, settings, api_client):
        """Test HHS AMS login url redirects."""
        response = api_client.get("/v1/login/ams")
        assert response.status_code == status.HTTP_302_FOUND

    def test_oidc_logout_with_token_and_hhs_handler(self, api_client):
        """Test logout redirect with token present."""
        factory = APIRequestFactory()
        view = LogoutRedirectOIDC.as_view()
        request = factory.get("/v1/logout/oidc")
        request.session = api_client.session
        request.session["token"] = "testtoken"
        request.session["ams"] = True
        response = view(request)
        assert response.status_code == status.HTTP_302_FOUND

    def test_login_with_valid_state_and_code(
        self,
        states_factory,
        req_factory,
        user,
    ):
        """Test login with state and code."""
        request = req_factory
        request = create_session(request, states_factory)
        user.username = "test_existing@example.com"
        user.save()

        view = TokenAuthorizationAMS.as_view()
        response = view(request)
        assert response.status_code == status.HTTP_302_FOUND

    def test_login_with_existing_token(
        self,
        states_factory,
        req_factory
    ):
        """Login should proceed when token already exists."""
        view = TokenAuthorizationAMS.as_view()
        request = req_factory
        request.session["token"] = "testtoken"
        request = create_session(request, states_factory)
        response = view(request)
        assert response.status_code == status.HTTP_302_FOUND

    def test_login_with_general_exception(
        self,
        states_factory,
        req_factory
    ):
        """Test login with state and code."""
        states = states_factory
        request = req_factory
        view = TokenAuthorizationAMS.as_view()

        # A custom session will throw a general exception
        request.session = {}
        request = create_session(request, states)
        response = view(request)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {
            "error": (
                "Email verified, but experienced internal issue "
                "with login/registration."
            )
        }

    def test_login_with_inactive_user(
        self,
        inactive_user,
        states_factory,
        mock_decode,
        requests_mock,
        req_factory
    ):
        """
        Login with inactive user should error and return message.

        Note this test considers the `is_active` field, and *not* `deactivated`,
        which are different.
        """
        request = req_factory

        inactive_user.username = "test_inactive@example.com"
        inactive_user.save()

        requests_mock.post(TestLoginAMS.mock_configuration["userinfo_endpoint"],
                           json={"email": "test_inactive@example.com"})

        mock_decode.return_value = decoded_token(
            "test_inactive@example.com",
            states_factory['nonce'],
        )

        view = TokenAuthorizationAMS.as_view()
        request = create_session(request, states_factory)
        response = view(request)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data == {
            "error": f'Login failed, user account is inactive: {inactive_user.username}'
        }

    def test_login_with_existing_user(
        self,
        user,
        mock_decode,
        states_factory,
        req_factory
    ):
        """Login should work with existing user."""
        states = states_factory
        request = req_factory
        request = create_session(request, states_factory)

        user.username = "test_existing@example.com"
        user.save()
        view = TokenAuthorizationAMS.as_view()
        mock_decode.return_value = decoded_token(
            "test_existing@example.com",
            states["nonce"],
        )

        response = view(request)
        assert response.status_code == status.HTTP_302_FOUND

    def test_login_with_old_email(
        self,
        mock_decode,
        states_factory,
        req_factory,
        user
    ):
        """Login should work with existing user."""
        user.username = "test_old_email@example.com"
        user.save()
        states = states_factory
        request = req_factory
        request = create_session(request, states_factory)
        view = TokenAuthorizationAMS.as_view()
        mock_decode.return_value = decoded_token(
            "test_new_email@example.com",
            states["nonce"],
        )
        response = view(request)
        # Ensure the user's username was updated with new email.
        assert User.objects.filter(username="test_new_email@example.com").exists()
        assert response.status_code == status.HTTP_302_FOUND

    def test_login_with_initial_superuser(
        self,
        mock_decode,
        states_factory,
        req_factory,
        settings,
        user
    ):
        """Login should work with existing user."""
        # How to set os vars for sudo su??
        test_username = "test_superuser@example.com"
        settings.DJANGO_SUPERUSER_NAME = test_username
        user.username = test_username
        user.login_gov_uuid = None
        user.save()
        states = states_factory
        request = req_factory
        request = create_session(request, states_factory)
        mock_decode.return_value = decoded_token(test_username, states["nonce"])
        view = TokenAuthorizationAMS.as_view()
        response = view(request)

        user = User.objects.get(username=test_username)
        assert str(user.login_gov_uuid) == mock_decode.return_value["sub"]
        assert response.status_code == status.HTTP_302_FOUND

    def test_login_with_expired_token(
        self,
        mock_decode,
        states_factory,
        req_factory,
    ):
        """Login should proceed when token already exists."""
        request = req_factory
        request = create_session(request, states_factory)
        mock_decode.side_effect = jwt.ExpiredSignatureError()

        view = TokenAuthorizationAMS.as_view()
        response = view(request)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data == {"error": "The token is expired."}

    def test_login_with_bad_validation_code(
        self,
        states_factory,
        req_factory,
        requests_mock
    ):
        """Login should error with a bad validation code."""
        request = req_factory
        request = create_session(request, states_factory)

        requests_mock.post(TestLoginAMS.mock_configuration["token_endpoint"], json={}, status_code=400)

        view = TokenAuthorizationAMS.as_view()
        response = view(request)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {
            "error": "Invalid Validation Code Or OpenID Connect Authenticator Down!"
        }

    def test_login_with_bad_nonce_and_state(
        self,
        mock_decode,
        states_factory,
        req_factory,
    ):
        """Login should error with a bad nonce and state."""
        request = req_factory
        request = create_session(request, states_factory)
        view = TokenAuthorizationAMS.as_view()
        request.session["state_nonce_tracker"] = {
            "nonce": "badnonce",
            "state": "badstate",
            "added_on": time.time(),
        }
        with pytest.raises(SuspiciousOperation):
            view(request)

    def test_login_with_email_unverified(
        self,
        mock_decode,
        states_factory,
        req_factory,
    ):
        """Login should fail with unverified email."""
        states = states_factory
        request = req_factory
        request = create_session(request, states_factory)
        mock_decode.return_value = decoded_token(
            "test@example.com",
            states['nonce'],
            email_verified=False
        )
        view = TokenAuthorizationAMS.as_view()
        response = view(request)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"error": "Unverified email!"}


def test_login_gov_redirect(api_client):
    """Test login.gov login url redirects."""
    response = api_client.get("/v1/login/dotgov")
    assert response.status_code == status.HTTP_302_FOUND


def test_oidc_logout_without_token(api_client):
    """Test logout redirect with token missing."""
    response = api_client.get("/v1/logout/oidc")
    assert response.status_code == status.HTTP_302_FOUND


def test_oidc_logout_with_token(api_client):
    """Test logout redirect with token present."""
    factory = APIRequestFactory()
    view = LogoutRedirectOIDC.as_view()
    request = factory.get("/v1/logout/oidc")
    request.session = api_client.session
    request.session["token"] = "testtoken"
    response = view(request)
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_auth_update(api_client, user):
    """Test session update."""
    api_client.login(username=user.username, password="test_password")

    api_client.get("/v1/auth_check")
    c1 = api_client.cookies.get("id_token")
    e1 = datetime.datetime.strptime(c1["expires"], "%a, %d %b %Y %H:%M:%S %Z")
    time.sleep(1)

    api_client.get("/v1/auth_check")
    c2 = api_client.cookies.get("id_token")
    e2 = datetime.datetime.strptime(c2["expires"], "%a, %d %b %Y %H:%M:%S %Z")

    assert e1 < e2


@pytest.mark.django_db
def test_logout(api_client, user):
    """Test logout."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get("/v1/logout")
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_login_without_code(api_client):
    """Test login redirects without code."""
    response = api_client.get("/v1/login/", {"state": "dummy"})
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_login_fails_without_state(api_client):
    """Test login redirects without state."""
    response = api_client.get("/v1/login/", {"code": "dummy"})
    assert response.status_code == status.HTTP_302_FOUND


def decoded_token(
    email,
    nonce,
    sub="b2d2d115-1d7e-4579-b9d6-f8e84f4f56ca",
    email_verified=True
):
    """Generate a token dictionary as part of DRY."""
    decoded_token = {
        "email": email,
        "email_verified": email_verified,
        "nonce": nonce,
        "iss": "https://idp.int.identitysandbox.gov",
        "sub": sub,
        "verified_at": 1577854800,
    }
    return decoded_token


def create_session(request, states):
    """Generate a client session as part of DRY."""
    request.session["state_nonce_tracker"] = {
        "nonce": states['nonce'],
        "state": states['state'],
        "added_on": time.time(),
    }
    return request


@pytest.mark.django_db
class TestLogin:
    """Associate a set of related tests into a class for shared mock fixtures."""

    @pytest.fixture()
    def mock(self, states_factory, mocker, mock_token):
        """Generate all the mock-up data structs needed for API tests."""
        mock_post = mocker.patch("tdpservice.users.api.login.requests.post")
        token = {
            "access_token": "hhJES3wcgjI55jzjBvZpNQ",
            "token_type": "Bearer",
            "expires_in": 3600,
            "id_token": mock_token,
        }
        mock_post.return_value = MockRequest(data=token)
        mock_decode = mocker.patch("tdpservice.users.api.login.jwt.decode")

        mock_decode.return_value = decoded_token(
            "test@example.com",
            states_factory['nonce']
        )

        yield mock_post, mock_decode

    def test_login_with_valid_state_and_code(
        self,
        patch_login_gov_jwt_key,
        states_factory,
        mock,
        req_factory
    ):
        """Test login with state and code."""
        request = req_factory
        request = create_session(request, states_factory)
        view = TokenAuthorizationLoginDotGov.as_view()
        response = view(request)
        assert response.status_code == status.HTTP_302_FOUND

    def test_login_with_existing_token(
        self,
        patch_login_gov_jwt_key,
        states_factory,
        mock,
        req_factory
    ):
        """Login should proceed when token already exists."""
        view = TokenAuthorizationLoginDotGov.as_view()
        request = req_factory
        request.session["token"] = "testtoken"
        request = create_session(request, states_factory)
        response = view(request)
        assert response.status_code == status.HTTP_302_FOUND

    def test_login_with_general_exception(
        self,
        patch_login_gov_jwt_key,
        states_factory,
        mock,
        req_factory
    ):
        """Test login with state and code."""
        states = states_factory
        request = req_factory
        view = TokenAuthorizationLoginDotGov.as_view()

        # A custom session will throw a general exception
        request.session = {}
        request = create_session(request, states)
        response = view(request)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {
            "error": (
                "Email verified, but experienced internal issue "
                "with login/registration."
            )
        }

    def test_login_with_inactive_user(
        self,
        inactive_user,
        patch_login_gov_jwt_key,
        states_factory,
        mock,
        req_factory
    ):
        """
        Login with inactive user should error and return message.

        Note this test considers the `is_active` field, and *not* `deactivated`,
        which are different.
        """
        request = req_factory
        mock_post, mock_decode = mock

        inactive_user.username = "test_inactive@example.com"
        inactive_user.save()

        mock_decode.return_value = decoded_token(
            "test_inactive@example.com",
            states_factory['nonce'],
            sub=inactive_user.login_gov_uuid
        )
        view = TokenAuthorizationLoginDotGov.as_view()
        request = create_session(request, states_factory)
        response = view(request)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data == {
            "error": f'Login failed, user account is inactive: {inactive_user.username}'
        }

    def test_login_with_existing_user(
        self,
        user,
        patch_login_gov_jwt_key,
        mock,
        states_factory,
        req_factory
    ):
        """Login should work with existing user."""
        states = states_factory
        request = req_factory
        request = create_session(request, states_factory)

        user.username = "test_existing@example.com"
        user.save()
        view = TokenAuthorizationLoginDotGov.as_view()
        mock_post, mock_decode = mock
        mock_decode.return_value = decoded_token(
            "test_existing@example.com",
            states["nonce"],
            sub=user.login_gov_uuid
        )

        response = view(request)
        assert response.status_code == status.HTTP_302_FOUND

    def test_login_with_old_email(
        self,
        mock,
        states_factory,
        req_factory,
        patch_login_gov_jwt_key,
        user
    ):
        """Login should work with existing user."""
        user.username = "test_old_email@example.com"
        user.save()
        states = states_factory
        request = req_factory
        request = create_session(request, states_factory)
        view = TokenAuthorizationLoginDotGov.as_view()
        mock_post, mock_decode = mock
        mock_decode.return_value = decoded_token(
            "test_new_email@example.com",
            states["nonce"],
            sub=user.login_gov_uuid
        )
        response = view(request)
        # Ensure the user's username was updated with new email.
        assert User.objects.filter(username="test_new_email@example.com").exists()
        assert response.status_code == status.HTTP_302_FOUND

    def test_login_with_initial_superuser(
        self,
        mock,
        states_factory,
        req_factory,
        patch_login_gov_jwt_key,
        settings,
        user
    ):
        """Login should work with existing user."""
        # How to set os vars for sudo su??
        test_username = "test_superuser@example.com"
        settings.DJANGO_SUPERUSER_NAME = test_username
        user.username = test_username
        user.login_gov_uuid = None
        user.save()
        states = states_factory
        request = req_factory
        request = create_session(request, states_factory)
        mock_post, mock_decode = mock
        mock_decode.return_value = decoded_token(test_username, states["nonce"])
        view = TokenAuthorizationLoginDotGov.as_view()
        response = view(request)

        user = User.objects.get(username=test_username)
        assert str(user.login_gov_uuid) == mock_decode.return_value["sub"]
        assert response.status_code == status.HTTP_302_FOUND

    def test_login_with_expired_token(
        self,
        mock,
        states_factory,
        req_factory,
        patch_login_gov_jwt_key
    ):
        """Login should proceed when token already exists."""
        request = req_factory
        request = create_session(request, states_factory)
        mock_post, mock_decode = mock
        mock_decode.side_effect = jwt.ExpiredSignatureError()

        view = TokenAuthorizationLoginDotGov.as_view()
        response = view(request)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data == {"error": "The token is expired."}

    def test_login_with_bad_validation_code(
        self,
        mock,
        states_factory,
        req_factory,
        patch_login_gov_jwt_key
    ):
        """Login should error with a bad validation code."""
        request = req_factory
        request = create_session(request, states_factory)
        mock_post, mock_decode = mock
        mock_post.return_value = MockRequest(
            data={}, status_code=status.HTTP_400_BAD_REQUEST
        )
        view = TokenAuthorizationLoginDotGov.as_view()
        response = view(request)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {
            "error": "Invalid Validation Code Or OpenID Connect Authenticator Down!"
        }

    def test_login_with_bad_nonce_and_state(
        self,
        mock,
        states_factory,
        req_factory,
        patch_login_gov_jwt_key
    ):
        """Login should error with a bad nonce and state."""
        request = req_factory
        request = create_session(request, states_factory)
        mock_post, mock_decode = mock
        view = TokenAuthorizationLoginDotGov.as_view()
        request.session["state_nonce_tracker"] = {
            "nonce": "badnonce",
            "state": "badstate",
            "added_on": time.time(),
        }
        with pytest.raises(SuspiciousOperation):
            view(request)

    def test_login_with_email_unverified(
        self,
        mock,
        states_factory,
        req_factory,
        patch_login_gov_jwt_key
    ):
        """Login should fail with unverified email."""
        states = states_factory
        request = req_factory
        request = create_session(request, states_factory)
        mock_post, mock_decode = mock
        mock_decode.return_value = decoded_token(
            "test@example.com",
            states['nonce'],
            email_verified=False
        )
        view = TokenAuthorizationLoginDotGov.as_view()
        response = view(request)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"error": "Unverified email!"}


@pytest.mark.django_db
def test_login_fails_with_bad_data(api_client):
    """Test login fails with bad data."""
    response = api_client.get("/v1/login/", {"code": "dummy", "state": "dummy"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_response_internal(user):
    """Test response internal works."""
    response = response_internal(
        user, status_message="hello", id_token={"fake": "stuff"}
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_generate_jwt_from_jwks(mocker):
    """Test JWT generation."""
    mock_get = mocker.patch("requests.get")
    jwk = {
        "kty": "EC",
        "crv": "P-256",
        "x": "f83OJ3D2xF1Bg8vub9tLe1gHMzV76e8Tus9uPHvRVEU",
        "y": "x_FEzRu9m36HLN_tue659LNpXW6pCyStikYjKIWI5a0",
        "kid": "Public key used in JWS spec Appendix A.3 example",
    }
    mock_get.return_value = MockRequest(data={"keys": [jwk]})
    assert generate_jwt_from_jwks("/v1/login") is not None


@pytest.mark.django_db
def test_generate_client_assertion_pem(patch_login_gov_jwt_key):
    """Test client assertion generation with PEM encoded key."""
    assert generate_client_assertion() is not None


@pytest.mark.django_db
def test_generate_client_assertion_base64(settings, test_private_key):
    """Test client assertion generation with Base64 key."""
    from base64 import b64encode
    settings.LOGIN_GOV_JWT_KEY = b64encode(test_private_key)
    utf8_jwt_key = generate_client_assertion()
    assert utf8_jwt_key is not None


@pytest.mark.django_db
def test_generate_token_endpoint_parameters(patch_login_gov_jwt_key):
    """Test token endpoint parameter generation."""
    token_params = generate_token_endpoint_parameters("test_code")
    assert "code=test_code" in token_params
    assert "grant_type=authorization_code" in token_params

    # Test specific login.gov options
    options = {
        "client_assertion": generate_client_assertion(),
        "client_assertion_type": "sometype"
    }
    login_gov_token_params = generate_token_endpoint_parameters("test_code", options)
    assert "code=test_code" in login_gov_token_params
    assert "client_assertion" in login_gov_token_params
    assert "client_assertion_type" in login_gov_token_params
    assert "grant_type=authorization_code" in login_gov_token_params


def test_token_auth_decode_payload(mock_token):
    """Test ID token decoding functionality."""
    decoded_token = TokenAuthorizationLoginDotGov.decode_jwt(
        mock_token,
        "",
        "",
        "",
        # Since these tokens are short lived our MOCK_TOKEN used for tests
        # is expired and would need to be refreshed on each test run, to work
        # around that we will disable signature verification for this test.
        # TODO: Consider writing code to generate MOCK_TOKEN on demand
        options={'verify_signature': False}
    )

    # Assert the token was decoded correctly and contains necessary properties
    assert decoded_token is not None
    assert 'nonce' in decoded_token
    assert 'sub' in decoded_token
    assert 'login.gov' in decoded_token.get('iss', '')


def test_missing_django_superuser():
    """Test that an error is raised when env var DJANGO_SU_NAME is missing."""
    os.environ['DJANGO_SU_NAME'] = ''
    with pytest.raises(ImproperlyConfigured):
        get_required_env_var_setting('DJANGO_SU_NAME')


def test_missing_jwt_key():
    """Test that an error is raised when env var JWT_KEY is missing."""
    os.environ['JWT_KEY'] = ''
    with pytest.raises(ImproperlyConfigured):
        get_required_env_var_setting('JWT_KEY')
