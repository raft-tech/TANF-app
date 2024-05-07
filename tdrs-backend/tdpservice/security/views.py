"""Views for the security app."""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.decorators import user_passes_test
from tdpservice.users.models import User
from rest_framework.authtoken.models import Token
from rest_framework import exceptions
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import TokenAuthentication
from datetime import datetime
import pytz
from datetime import timedelta
from django.conf import settings

import logging

logger = logging.getLogger(__name__)


def can_get_new_token(user):
    """Check if user can get a new token."""
    return user.is_authenticated and user.is_ofa_sys_admin


def token_is_valid(token):
    """Check if token is valid."""
    utc_now = datetime.now()
    utc_now = utc_now.replace(tzinfo=pytz.utc)
    if token.created < (utc_now - timedelta(hours=settings.TOKEN_EXPIRATION_HOURS)):
        raise exceptions.AuthenticationFailed("Token has expired")
    return token is not None


@user_passes_test(can_get_new_token, login_url="/login/")
@api_view(["GET"])
def generate_new_token(request):
    """Generate new token for the API user."""
    if request.method == "GET":
        user = User.objects.get(username=request.user)
        token, created = Token.objects.get_or_create(user=user)
        if token_is_valid(token):
            return Response(str(token))
        else:
            token.delete()
            token = Token.objects.create(user=user)
            return Response(str(token))


# have to use ExpTokenAuthentication in settings.py instead of TokenAuthentication
class ExpTokenAuthentication(TokenAuthentication):
    """Custom token authentication class that checks if token is expired."""

    # see https://github.com/encode/django-rest-framework/blob/master/rest_framework/authentication.py

    def authenticate_credentials(self, key):
        """Authenticate the credentials."""
        model = self.get_model()
        try:
            token = model.objects.select_related("user").get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_("User inactive or deleted."))

        if not token_is_valid(token):
            raise exceptions.AuthenticationFailed(_("Token expired."))

        return (token.user, token)
