"""Views for OIDC Keycloak integration"""

from mozilla_django_oidc.views import OIDCAuthenticationRequestView

class LoginGovKeycloakAuthView(OIDCAuthenticationRequestView):
    """OIDC view for Login.gov that includes the `kc_idp_hint` for Login.gov and the required `acr_values` for IAL1."""
    kc_idp_hint = 'login-gov'
    acr_values = 'http://idmanagement.gov/ns/assurance/ial/1'

    def get_extra_params(self, request):
        """Add kc_idp_hint and acr_values for Login.gov."""
        params = super().get_extra_params(request)
        params['kc_idp_hint'] = self.kc_idp_hint
        params['acr_values'] = self.acr_values
        return params

class AcfAmsKeycloakAuthView(OIDCAuthenticationRequestView):
    """OIDC view for ACF AMS that includes the `kc_idp_hint` for ACF AMS."""
    kc_idp_hint = 'acf-ams'

    def get_extra_params(self, request):
        """Add kc_idp_hint for ACF AMS."""
        params = super().get_extra_params(request)
        params['kc_idp_hint'] = self.kc_idp_hint
        return params
