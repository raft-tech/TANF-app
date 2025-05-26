from mozilla_django_oidc.views import OIDCAuthenticationRequestView

class FixedHintOIDCAuthenticationRequestView(OIDCAuthenticationRequestView):
    """
    An OIDC view that allows specifying a fixed `kc_idp_hint`
    to be passed to Keycloak. This hint is used by Keycloak to pre-select
    an upstream Identity Provider.

    Subclasses should set the `fixed_kc_idp_hint` attribute.
    """
    fixed_kc_idp_hint = None  # Must be overridden by subclasses, e.g., 'login-gov' or 'acf-ams'

    def get_extra_params(self, request):
        """Add the kc_idp_hint to the authentication request parameters."""
        params = super().get_extra_params(request)
        if self.fixed_kc_idp_hint:
            params['kc_idp_hint'] = self.fixed_kc_idp_hint
        return params

class LoginGovHintView(FixedHintOIDCAuthenticationRequestView):
    """
    OIDC view for Login.gov that includes the `kc_idp_hint` for Login.gov
    and the required `acr_values` for IAL1.
    """
    fixed_kc_idp_hint = 'login-gov'
    acr_value_login_gov = 'http://idmanagement.gov/ns/assurance/ial/1'

    def get_extra_params(self, request):
        """Add kc_idp_hint (from super) and acr_values for Login.gov."""
        params = super().get_extra_params(request)  # This will call FixedHintOIDCAuthenticationRequestView.get_extra_params
        if self.acr_value_login_gov:
            params['acr_values'] = self.acr_value_login_gov
        return params

class AcfAmsHintView(FixedHintOIDCAuthenticationRequestView):
    """
    OIDC view for ACF AMS that includes the `kc_idp_hint` for ACF AMS.
    """
    fixed_kc_idp_hint = 'acf-ams'
