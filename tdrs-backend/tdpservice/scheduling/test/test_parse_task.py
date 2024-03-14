import pytest
from tdpservice.email.helpers.data_file import send_data_processed_email
from django.core import mail
from tdpservice.scheduling.parser_task import parse as parse_task
from tdpservice.parsers.models import DataFileSummary
from tdpservice.parsers import util

# just trying to get the test to pass
from tdpservice.parsers.models import ParserError, ParserErrorCategoryChoices, DataFileSummary
from tdpservice.search_indexes.models.tanf import TANF_T1, TANF_T2, TANF_T3, TANF_T4, TANF_T5, TANF_T6, TANF_T7
from tdpservice.search_indexes.models.ssp import SSP_M1, SSP_M2, SSP_M3, SSP_M4, SSP_M5, SSP_M6, SSP_M7
from tdpservice.parsers.test.factories import DataFileSummaryFactory
from tdpservice.data_files.models import DataFile


@pytest.fixture
def dfs():
    """Fixture for DataFileSummary."""
    return DataFileSummaryFactory.create()

@pytest.fixture
def good_datafile(stt_user, stt):
    """Fixture for small_correct_file."""
    return util.create_test_datafile('small_correct_file.txt', stt_user, stt)

@pytest.fixture
def bad_datafile(stt_user, stt):
    """Fixture for small_correct_file."""
    return util.create_test_datafile('small_bad_tanf_s1.txt', stt_user, stt)

@pytest.mark.django_db
def test_data_processed_email(good_datafile):
    """Ensure email is sent when datafile is processed."""
    data_file = good_datafile
    data_file.save()
    parse_task(data_file.id)
    #query all DataFileSummary objects matching the data_file.id
    data_file_summary = DataFileSummary.objects.filter(datafile=data_file.id)

    send_data_processed_email(data_file, data_file_summary[0].status)
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Data Processed"

@pytest.mark.django_db
def test_data_processed_email_with_errors(bad_datafile):
    """Ensure email is sent when datafile is processed with errors."""
    data_file = bad_datafile
    parse_task(data_file.id)
    #query all DataFileSummary objects matching the data_file.id
    data_file_summary = DataFileSummary.objects.filter(datafile=data_file.id)

    send_data_processed_email(data_file, data_file_summary[0].status)
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Data Processed with Errors"