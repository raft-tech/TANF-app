"""Module for testing the automated account emails."""

import pytest
import tdpservice
from tdpservice.users.models import User

@pytest.mark.django_db
def test_deactivated_user_sends_email(user, mocker):
    """"""
    mocker.patch(
        'tdpservice.email.email.mail.delay',
        return_value=True
    )
    user = User.objects.get(username=user.username)
    user.account_approval_status = 'Deactivated'
    user.save()

    assert user.account_approval_status == 'Deactivated'
    tdpservice.email.email.mail.delay.assert_called_once_with()    
