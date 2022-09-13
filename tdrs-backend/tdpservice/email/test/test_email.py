from tdpservice.email.email import send_email
from django.core import mail
from django.test import TestCase

"""
This is a Django test case that tests the send_email function in the email.py file.
"""

class EmailTest(TestCase):
    """Email test class."""

    def test_send_email(self):
        """Test email."""
        subject = "Test email"
        message = "This is a test email."
        sender = "test_user@hhs.gov"
        recipient_list = ["test_user@hhs.gov"]

        send_email(subject, message, sender, recipient_list)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)
