import uuid

import pytest
from rest_framework import status

from .models import ReportFile


# Create your tests here.
@pytest.mark.django_db
def test_create_report_file_entry(api_client, user):
    """Test profile data cannot be set if last name field is missing."""
    api_client.login(username=user.username, password="test_password")
    data = {
        'original_name':"report.txt",
        'slug':uuid.uuid4(),
        'user':user.id,
        'year': 2020,
        'section':1
    }
    response = api_client.post("/v1/reports/", data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert ReportFile.objects.filter(
        slug=data['slug'],
        year=data['year'],
        section=data['section'],
        version=1,
        user=user,
    ).exists()
