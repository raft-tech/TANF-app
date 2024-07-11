from django.conf import settings
from unittest import mock
from tdpservice.users.api.login_redirect_oidc import LoginRedirectAMS

@mock.patch("requests.get")
def test_get_ams_configuration(requests_get_mock):
    """Test the LoginRedirectAMS class."""
    requests_get_mock.return_value.status_code = 200
    requests_get_mock.return_value.json.return_value = {"key": "test"}
    returned_value = LoginRedirectAMS.get_ams_configuration()
    assert returned_value == {"key": "test"}

    # Test if the configuration is not returned
    requests_get_mock.return_value.status_code = 500
    returned_value = LoginRedirectAMS.get_ams_configuration()
    assert returned_value is None

@mock.patch("requests.get")
@mock.patch("secrets.token_hex")
def test_LoginRedirectAMS_get(secrets_token_hex_mock, requests_get_mock):
    """Test the LoginRedirectAMS class."""
    class DummyRequest:
        session = {
            "state_nonce_tracker": "dummy_state_nonce_tracker"
        }

    requests_get_mock.return_value.status_code = 200
    requests_get_mock.return_value.json.return_value = {"authorization_endpoint": "dummy_authorization_endpoint"}
    
    secrets_token_hex_mock.return_value = "dummy_state_nonce"
    
    login_redirect_ams = LoginRedirectAMS()
    
    response = login_redirect_ams.get(DummyRequest)
    assert response.url == "dummy_authorization_endpoint?client_id=&nonce=dummy_state_nonce&redirect_uri=http%3A" +\
        "%2F%2Flocalhost%3A3000%2Fv1%2Foidc%2Fams&response_type=code&state=dummy_state_nonce&scope=openid+email"
    

    # Test if the AMS server is down
    requests_get_mock.return_value.status_code = 500
    login_redirect_ams = LoginRedirectAMS()
    response = login_redirect_ams.get("request")
    assert response.status_code == 500

    