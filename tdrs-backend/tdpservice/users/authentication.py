"""Define custom authentication class."""

from django.contrib.auth import get_user_model


class CustomAuthentication:
    """Define authentication and get user functions for custom authentication."""

    def authenticate(self, username=None):
        """Authenticate user with the request and username."""
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        """Get user by the user id."""
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate_header(self, request):
        return 'Session'

    def enforce_csrf(self, request):
        'Enforce CSRF validation for session based authentication.'

        reason = CSRFCheck().process_view(request, None, (), {})
        if reason:
            # CSRF failed, bail with explicit error message
            raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)
