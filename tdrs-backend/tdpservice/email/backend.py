"""Override Emailbackend to inject DKIM signatures into the message body."""

import smtplib
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings
from django.core.mail.message import sanitize_address
from dkimpy import DKIM


class DKIMEmailBackend(EmailBackend):
    """Override EmailBackend to inject DKIM signature into the message body."""

    def _send(self, email_message):
        """Override EmailBackend._send."""
        if not email_message.recipients():
            return False
        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = sanitize_address(email_message.from_email, encoding)
        recipients = [
            sanitize_address(addr, encoding) for addr in email_message.recipients()
        ]
        message = email_message.message().as_string()

        dkim = DKIM()
        # signature = "dkim signature from message_string"
        signature = dkim.sign(
            message,
            settings.EMAIL_DKIM_DOMAIN,
            settings.EMAIL_DKIM_PRIVATE_KEY,
            # signature_algorithm=None,
            # identity=None,
            # canonicalize=('relaxed', 'simple'),
            # include_headers=None,
            # length=False
        )
        try:
            self.connection.sendmail(
                from_email, recipients, signature+message
            )
        except smtplib.SMTPException:
            if not self.fail_silently:
                raise
            return False
        return True
