"""Integration test(s) for clamav-rest operations."""

import pytest

from tdpservice.data_files.test.factories import DataFileFactory


@pytest.fixture()
def upload_file():
    """Fixture for test upload file."""
    return DataFileFactory()


@pytest.mark.django_db
def test_upload_server(upload_file):
    """Test upload file."""
    assert upload_file.original_filename == 'data_file.txt'
