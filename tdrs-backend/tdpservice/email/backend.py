import smtplib
from typing import Any
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from django.core.mail.message import sanitize_address
import sendgrid
from sendgrid.helpers.mail import Mail, From, To, Subject, PlainTextContent, HtmlContent


class SendgridEmailBackend(BaseEmailBackend):
    """asdfasdf."""

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently, **kwargs)
        self.connection = None

    def open(self):
        """
        Ensure an open connection to the email server. Return whether or not a
        new connection was required (True or False) or None if an exception
        passed silently.
        """
        if self.connection:
            # Nothing to do if the connection is already open.
            return False

        try:
            self.connection = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
            return True
        except OSError:
            if not self.fail_silently:
                raise

    def close(self):
        """Close the connection to the email server."""
        if self.connection is None:
            return

        self.connection = None

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        if not email_messages:
            return 0
        with self._lock:
            new_conn_created = self.open()
            if not self.connection or new_conn_created is None:
                # We failed silently on open().
                # Trying to send would be pointless.
                return 0
            num_sent = 0
            try:
                for message in email_messages:
                    sent = self._send(message)
                    if sent:
                        num_sent += 1
            finally:
                if new_conn_created:
                    self.close()
        return num_sent
        pass

    def _send(self, email_message):
        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = From(sanitize_address(email_message.from_email, encoding))
        to_emails = [To(sanitize_address(addr, encoding)) for addr in email_message.recipients()]
        subject = Subject(email_message.subject)
        content = PlainTextContent(email_message.message)
        html_content = HtmlContent(email_message.html_message)

        mail = Mail(
            from_email=from_email,
            to_emails=to_emails,
            subject=subject,
            content=content,
            html_content=html_content)

        response = self.connection.client.mail.send.post(
            request_body=mail.get()
        )

        if response.status_code == 200:
            return True
        
        return False