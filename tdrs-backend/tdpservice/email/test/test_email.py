from tdpservice.email import send_email
from django.core import mail
from django.test import TestCase

class EmailTest(TestCase):

    def test_send_email(self):
        """Test email"""
        subject = "Test email"
        message = "This is a test email."
        sender = "test_user@hhs.gov"
        recipient_list = ["foo"]

        send_email(subject, message, sender, recipient_list)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)
        