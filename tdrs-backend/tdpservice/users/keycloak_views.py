"""Views for OIDC Keycloak integration"""

from django.conf import settings

from mozilla_django_oidc.views import OIDCAuthenticationRequestView


class LoginGovKeycloakAuthView(OIDCAuthenticationRequestView):
    """OIDC view for Login.gov that includes the `kc_idp_hint` for Login.gov and the required `acr_values` for IAL1."""

    kc_idp_hint = "login-gov"
    acr_values = "http://idmanagement.gov/ns/assurance/ial/1"

    def get_extra_params(self, request):
        """Add kc_idp_hint and acr_values for Login.gov."""
        params = super().get_extra_params(request)
        params["kc_idp_hint"] = self.kc_idp_hint
        params["acr_values"] = self.acr_values
        return params


class AcfAmsKeycloakAuthView(OIDCAuthenticationRequestView):
    """OIDC view for ACF AMS that includes the `kc_idp_hint` for ACF AMS."""

    kc_idp_hint = "acf-ams"

    def get_extra_params(self, request):
        """Add kc_idp_hint for ACF AMS."""
        params = super().get_extra_params(request)
        params["kc_idp_hint"] = self.kc_idp_hint
        return params


def logout_url(request):
    """Returns the Keycloak logout URL with appropriate kc_idp_hint for the user."""
    base_logout_url = settings.OIDC_OP_LOGOUT_ENDPOINT

    id_token = request.session.get("oidc_id_token", "")

    post_logout_redirect_uri = settings.LOGOUT_REDIRECT_URL
    # Build absolute URI
    if not post_logout_redirect_uri.startswith("http"):
        post_logout_redirect_uri = request.build_absolute_uri(post_logout_redirect_uri)

    # Build the logout URL with all parameters
    params = [
        f"id_token_hint={id_token}",
        f"post_logout_redirect_uri={post_logout_redirect_uri}",
        f"client_id={settings.OIDC_RP_CLIENT_ID}",
        f'kc_idp_hint={request.user.login_gov_uuid is not None and "login-gov" or "acf-ams"}',
    ]
    logout_url = f"{base_logout_url}?{'&'.join(params)}"
    return logout_url
