import pytest
from django.urls import reverse

@pytest.mark.django_db
class TestKeycloakViews:

    def test_login_gov_flow_initiation(self, client, settings):
        """Test that accessing the Login.gov Keycloak auth view initiates the OIDC flow correctly."""
        response = client.get(reverse('keycloak_login_gov'))

        assert response.status_code == 302
        redirect_location = response['Location']

        assert f"kc_idp_hint=login-gov" in redirect_location
        assert f"acr_values=http%3A%2F%2Fidmanagement.gov%2Fns%2Fassurance%2Fial%2F1" in redirect_location
        assert f"client_id={settings.OIDC_RP_CLIENT_ID}" in redirect_location
        assert "response_type=code" in redirect_location
        assert "scope=openid+profile+email" in redirect_location
        assert "state=" in redirect_location
        assert "nonce=" in redirect_location
        assert "redirect_uri=http%3A%2F%2Ftestserver%2Foidc%2Fcallback%2F" in redirect_location

    def test_acf_ams_flow_initiation(self, client, settings):
        """Test that accessing the ACF AMS Keycloak auth view initiates the OIDC flow correctly."""
        response = client.get(reverse('keycloak_login_ams'))

        assert response.status_code == 302
        redirect_location = response['Location']

        assert f"kc_idp_hint=acf-ams" in redirect_location
        assert f"acr_values=" not in redirect_location
        assert f"client_id={settings.OIDC_RP_CLIENT_ID}" in redirect_location
        assert "response_type=code" in redirect_location
        assert "scope=openid+profile+email" in redirect_location
        assert "state=" in redirect_location
        assert "nonce=" in redirect_location
        assert "redirect_uri=http%3A%2F%2Ftestserver%2Foidc%2Fcallback%2F" in redirect_location
