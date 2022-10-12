"""Test functions for deactivated ."""
from django.utils import timezone

import pytest
import tdpservice
from datetime import datetime, timedelta
from tdpservice.scheduling.tasks import check_for_accounts_needing_deactivation_warning

import logging
logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_deactivation_email_10_days(user, mocker):
    """Test that the check_for_accounts_needing_deactivation_warning task runs."""
    mocker.patch(
        'tdpservice.email.email_helper.send_deactivation_warning_email',
        return_value=None
    )

    user.last_login = datetime.now(tz=timezone.utc) - timedelta(days=170)
    user.first_name = 'UniqueName'
    user.save()
    check_for_accounts_needing_deactivation_warning()
    assert tdpservice.email.email_helper.send_deactivation_warning_email.called_once_with(users=[user], days=10)

@pytest.mark.django_db
def test_deactivation_email_3_days(user, mocker):
    """Test that the check_for_accounts_needing_deactivation_warning task runs."""
    mocker.patch(
        'tdpservice.email.email_helper.send_deactivation_warning_email',
        return_value=None
    )

    user.last_login = datetime.now(tz=timezone.utc) - timedelta(days=177)
    user.first_name = 'UniqueName'
    user.save()
    check_for_accounts_needing_deactivation_warning()
    assert tdpservice.email.email_helper.send_deactivation_warning_email.called_once_with(users=[user], days=3)

@pytest.mark.django_db
def test_deactivation_email_1_days(user, mocker):
    """Test that the check_for_accounts_needing_deactivation_warning task runs."""
    mocker.patch(
        'tdpservice.email.email_helper.send_deactivation_warning_email',
        return_value=None
    )

    user.last_login = datetime.now(tz=timezone.utc) - timedelta(days=179)
    user.first_name = 'UniqueName'
    user.save()
    check_for_accounts_needing_deactivation_warning()
    assert tdpservice.email.email_helper.send_deactivation_warning_email.called_once_with(users=[user], days=1)


@pytest.mark.django_db
def test_no_users_to_warn(user, mocker):
    """Test that the check_for_accounts_needing_deactivation_warning task runs."""
    mocker.patch(
        'tdpservice.email.email_helper.send_deactivation_warning_email',
        return_value=None
    )

    user.last_login = datetime.now() - timedelta(days=169)
    user.first_name = 'UniqueName'
    user.save()
    check_for_accounts_needing_deactivation_warning()
    tdpservice.email.email_helper.send_deactivation_warning_email.assert_not_called()
