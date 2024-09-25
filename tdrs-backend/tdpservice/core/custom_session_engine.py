"""Custom session engine for TDP."""

from django.contrib.sessions.backends import signed_cookies
from django.core import signing
import datetime
from django.conf import settings

class SessionStore(signed_cookies.SessionStore):
    """Custom session engine for TDP."""

    def __init__(self, session_key=None):
        """Initialize the custom session engine."""
        super().__init__(session_key)

    def load(self):
        """Load the session data from the database."""
        """
        Load the data from the key itself instead of fetching from some
        external data store. Opposite of _get_session_key(), raise BadSignature
        if signature fails.
        """

        try:
            return signing.loads(
                self.session_key,
                serializer=self.serializer,
                # This doesn't handle non-default expiry dates, see #19201
                max_age=datetime.timedelta(seconds=settings.SIGNED_COOKIE_EXPIRES),
                salt="django.contrib.sessions.backends.signed_cookies",
            )
        except Exception:
            # BadSignature, ValueError, or unpickling exceptions. If any of
            # these happen, reset the session.
            return {}

    def cycle_key(self):
        """Cycle the session key."""
        super().cycle_key()

    def create(self):
        """Create a new session."""
        # first check if the session exists
        super().create()

    def save(self, must_create=False):
        """Save the session data."""
        super().save(must_create)

    def exists(self, session_key):
        """Check if the session exists."""
        return super().exists(session_key)

    def delete(self, session_key=None):
        """Delete the session data."""
        super().delete(session_key)

    def _get_session_key(self):
        """Get the session key."""
        return super()._get_session_key()
