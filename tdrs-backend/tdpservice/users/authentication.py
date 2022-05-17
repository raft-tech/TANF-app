"""Define custom authentication class."""

import logging

from django.contrib.auth import get_user_model

from rest_framework.authentication import BaseAuthentication

logger = logging.getLogger(__name__)

class CustomAuthentication(BaseAuthentication):
    """Define authentication and get user functions for custom authentication."""

    @staticmethod
    def authenticate(username=None, login_gov_uuid=None, hhs_id=None, nextgen_xid=None):
        """Authenticate user with the request and username."""
        User = get_user_model()
        logging.debug("CustomAuthentication::authenticate:hhs_id {}".format(hhs_id))
        logging.debug("CustomAuthentication::authenticate:login_gov_uuid {}".format(login_gov_uuid))
        logging.debug("CustomAuthentication::authenticate:username {}".format(username))

        user_search = None
        id_type = None

        if hhs_id:
            id_type = "hhs_id"
            user_search = {hhs_id: hhs_id}
        elif nextgen_xid:
            id_type = "nextgen_xid"
            user_search = {nextgen_xid: nextgen_xid}
        else:
            id_type = "username"
            user_search = {username: username}
        try:
            return User.objects.get(**user_search)
        except User.DoesNotExist:
            # If below line also fails with User.DNE, will bubble up and return None
            if id_type != "username":
                user = User.objects.filter(username=username)
                user.update(**user_search)
                logging.debug("Updated user {} with {} {}.".format(username, id_type, user_search[id_type]))

    @staticmethod
    def get_user(user_id):
        """Get user by the user id."""
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
