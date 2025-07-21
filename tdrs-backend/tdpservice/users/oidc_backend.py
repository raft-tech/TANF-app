"""Custom OIDC Authentication Backend."""

import logging

from mozilla_django_oidc.auth import OIDCAuthenticationBackend

logger = logging.getLogger(__name__)


class CustomOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    """Custom OIDC Authentication Backend to ensure consistent user mapping."""

    def create_user(self, claims):
        """Create a new user from claims."""
        user = super().create_user(claims)
        user.username = claims.get("preferred_username", "")
        user.email = claims.get("email", "")
        user.login_gov_uuid = claims.get("sub", "")
        user.hhs_id = claims.get("hhs_id", "")
        user.save()

        return user

    def update_user(self, user, claims):
        """Update existing user with new claims."""
        user.username = claims.get("preferred_username", "")
        user.email = claims.get("email", "")
        user.save()

        return user
