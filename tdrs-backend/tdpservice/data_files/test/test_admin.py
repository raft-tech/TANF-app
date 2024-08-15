"""Test DataFileAdmin methods."""
import pytest
from django.contrib.admin.sites import AdminSite
#from django.contrib.admin.models import Admin

from tdpservice.data_files.admin import DataFileAdmin
from tdpservice.data_files.models import DataFile
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.parsers.test.factories import DataFileSummaryFactory
from django.conf import settings

@pytest.mark.django_db
def test_DataFileAdmin_status():
    """Test DataFileAdmin status method."""
    data_file = DataFileFactory()
    data_file_summary = DataFileSummaryFactory(datafile=data_file)
    data_file_admin = DataFileAdmin(DataFile, AdminSite())

    assert data_file_admin.status(data_file) == data_file_summary.status
    assert data_file_admin.case_totals(data_file) == data_file_summary.case_aggregates
    DOMAIN = settings.FRONTEND_BASE_URL
    assert data_file_admin.error_report_link(data_file) == \
        f"<a href='{DOMAIN}/admin/parsers/parsererror/?file={data_file.id}'>Parser Errors: 0</a>"

@pytest.mark.django_db
def test_by_submission_date(client):
    """Test by_submission_date method."""
    from django.db.models.query import QuerySet
    client.login(username='admin', password='password')
    url= '/admin/parsers/datafile/'
    # create fake queryset
    fake_query = DataFile.objects.all()
    data_file_admin = DataFileAdmin(DataFile, AdminSite())
    filter = DataFileAdmin.by_submission_date(None, {'Submission Day/Month/Year': '1'}, DataFile, DataFileAdmin)
    from django.contrib.admin.options import ModelAdmin
    assert data_file_admin.by_submission_date.title == 'Submission Date'
    assert data_file_admin.by_submission_date.parameter_name == 'Submission Day/Month/Year'
    assert data_file_admin.by_submission_date.lookups (filter, None, None) == [('1', 'Yesterday'), ('0', 'Today'), ('7', 'Past 7 days'), ('30', 'This month'), ('365', 'This year')]
    assert data_file_admin.by_submission_date.queryset(filter, None, fake_query).exists() == False
    df = DataFileFactory()
    from datetime import datetime, timezone, timedelta
    df.created_at = datetime.now(tz=timezone.utc) - timedelta(days=1)
    df.save()
    fake_query = DataFile.objects.all()
    assert data_file_admin.by_submission_date.queryset(filter, None, fake_query).exists() == True
    df.created_at = datetime.now(tz=timezone.utc) - timedelta(days=2)
    df.save()
    fake_query = DataFile.objects.all()
    assert data_file_admin.by_submission_date.queryset(filter, None, fake_query).exists() == False
