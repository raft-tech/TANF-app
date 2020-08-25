"""Login.gov/authorize is redirected to this endpoint to start a django user session."""

import os

from django.contrib.auth import get_user_model, login
from django.core.exceptions import SuspiciousOperation

import jwt
import requests
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from urllib.parse import urlencode, quote_plus

class TokenAuthorizationOIDC(ObtainAuthToken):
    """Define methods for handling login request from login.gov."""

    def get(self, request, *args, **kwargs):
        """Handle decoding auth token and authenticate user."""
        code = request.GET.get("code", None)
        state = request.GET.get("state", None)

        if code is None:
            return Response(
                {"error": "OIDC Code not found!"}, status=status.HTTP_400_BAD_REQUEST
            )
        if state is None:
            return Response(
                {"error": "OIDC State not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        # get the validation keys to confirm generated nonce and state
        nonce_and_state = utils.get_nonce_and_state(request)
        nonce_validator = nonce_and_state.get("nonce", "not_nonce")
        state_validator = nonce_and_state.get("state", "not_state")

        # build out the query string parameters
        # and full URL path for OIDC token endpoint
        token_params = utils.generate_token_endpoint_parameters(code)
        token_endpoint = os.environ["OIDC_OP_TOKEN_ENDPOINT"] + "?" + token_params
        token_response = requests.post(token_endpoint)

        if token_response.status_code == 200:
            token_data = token_response.json()
            id_token = token_data.get('id_token')
            cert_str = self.generateJWTFromJWKS()

            # issuer: issuer of the response
            # subject : UUID - not useful for login.gov set options to ignore this
            decoded_payload = jwt.decode(id_token,
                                         key=cert_str,
                                         issuer=os.environ['OIDC_OP_ISSUER'],
                                         audience=os.environ['CLIENT_ID'],
                                         algorithm='RS256',
                                         subject=None,
                                         access_token=None,
                                         options={'verify_nbf': False}
                                         )

            decoded_nonce = decoded_payload['nonce']

            if self.validNonceAndState(decoded_nonce, state, nonce_validator, state_validator) is False:
                msg = ('Could not validate nonce and state')
                raise SuspiciousOperation(msg)

            if decoded_payload['email_verified'] is True:
                try:
                    # get user from database if they exist. if not, create a new one
                    if 'token' not in request.session:
                        request.session['token'] = id_token

                    user = CustomAuthentication.authenticate(self, username=decoded_payload['email'])
                    if user is not None:
                        login(request, user, backend='tdpservice.users.authentication.CustomAuthentication')
                        return self.responseRedirect(id_token)

                    else:
                        User = get_user_model()
                        user = User.objects.create_user(decoded_payload['email'])
                        user.set_unusable_password()
                        user.save()

                        login(request, user, backend='tdpservice.users.authentication.CustomAuthentication')
                        return self.responseRedirect(id_token)

                except Exception:
                    return Response(
                        {'error': 'Email verfied, but experienced internal issue with login/registration.'},
                        status=status.HTTP_400_BAD_REQUEST)

        decoded_nonce = decoded_payload["nonce"]

        if not utils.validate_nonce_and_state(
            decoded_nonce, state, nonce_validator, state_validator
        ):
            msg = "Could not validate nonce and state"
            raise SuspiciousOperation(msg)

        if not decoded_payload["email_verified"]:
            return Response(
                {"error": "Unverified email!"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # get user from database if they exist. if not, create a new one
            if "token" not in request.session:
                request.session["token"] = id_token

            user = CustomAuthentication.authenticate(
                self, username=decoded_payload["email"]
            )
            if user is not None:
                login(
                    request,
                    user,
                    backend="tdpservice.users.authentication.CustomAuthentication",
                )
                return utils.response_internal(user, "User Found", id_token)

        nonce = openid_authenticity_tracker.get('nonce', None)
        validation_keys = {'state': state, 'nonce': nonce}
        return validation_keys

    """
    Redirects to web app with an httpOnly cookie.

    :param self: parameter to permit django python to call a method within its own class
    :param id_token: encoded token returned by login.gov/token
    """
    def responseRedirect(self, id_token):
        """Redirect to frontend with an httpOnly cookie to secure the session with the client."""
        response = HttpResponseRedirect(os.environ['FRONTEND_BASE_URL'] + '/login')
        response.set_cookie(
            'id_token', value=id_token, max_age=None, expires=None, path='/', domain=None, secure=False, httponly=True
        )
        return response
