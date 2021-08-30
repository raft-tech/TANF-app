"""Globally available pytest fixtures."""
import pytest
from django.contrib.admin.models import LogEntry
from django.contrib.admin.sites import AdminSite
from io import StringIO
import uuid

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import Group
from factory.faker import faker
from rest_framework.test import APIClient

from tdpservice.stts.test.factories import STTFactory, RegionFactory
from tdpservice.core.admin import LogEntryAdmin
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.users.test.factories import (
    UserFactory,
    AdminUserFactory,
    StaffUserFactory,
    STTUserFactory,
    InactiveUserFactory,
    AdminSTTUserFactory,
    DeactivatedUserFactory,
)

_faker = faker.Faker()


@pytest.fixture(scope="function")
def api_client():
    """Return an API client for testing."""
    return APIClient()


@pytest.fixture
def user():
    """Return a basic, non-admin user."""
    return UserFactory.create()


@pytest.fixture
def stt_user():
    """Return a user without an STT for STT tests."""
    return STTUserFactory.create()

@pytest.fixture
def ofa_admin_stt_user():
    """Return an admin user without an STT for Data File tests."""
    return AdminSTTUserFactory.create(groups=(Group.objects.get(name="OFA Admin"),))


@pytest.fixture
def ofa_admin():
    """Return an ofa admin user."""
    return UserFactory.create(groups=(Group.objects.get(name="OFA Admin"),))


@pytest.fixture
def ofa_system_admin():
    """Return on OFA System Admin user."""
    return UserFactory.create(groups=(Group.objects.get(name='OFA System Admin'),))


@pytest.fixture
def data_analyst():
    """Return a data analyst user."""
    return UserFactory.create(groups=(Group.objects.get(name="Data Analyst"),))


@pytest.fixture
def admin_user():
    """Return an admin user."""
    return AdminUserFactory.create()


@pytest.fixture
def staff_user():
    """Return a staff user."""
    return StaffUserFactory.create()


@pytest.fixture
def inactive_user():
    """Return an inactive user."""
    return InactiveUserFactory.create()


@pytest.fixture
def deactivated_user():
    """Return a user with an deactivated account."""
    return DeactivatedUserFactory.create()


@pytest.fixture
def stt():
    """Return an STT."""
    return STTFactory.create()


@pytest.fixture
def other_stt():
    """Return a secondary STT."""
    return STTFactory.create()


@pytest.fixture
def region():
    """Return a region."""
    return RegionFactory.create()


@pytest.fixture
def fake_file_name():
    """Generate a random, but valid file name ending in .txt."""
    return _faker.file_name(extension='txt')


@pytest.fixture
def fake_file():
    """Generate an in-memory file-like object with random contents."""
    return StringIO(_faker.sentence())


@pytest.fixture
def infected_file():
    """Generate an EICAR test file that will be treated as an infected file.

    https://en.wikipedia.org/wiki/EICAR_test_file
    """
    return StringIO(
        r'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
    )


def create_temporary_file(file, file_name) -> SimpleUploadedFile:
    """Create a temporary file with an explicit name from a given string."""
    file.seek(0)
    file_contents = file.read().encode()
    return SimpleUploadedFile(file_name, file_contents)


@pytest.fixture
def data_file(fake_file, fake_file_name):
    """Temporary file for testing file uploads."""
    return create_temporary_file(fake_file, fake_file_name)


@pytest.fixture
def other_data_file(fake_file, fake_file_name):
    """Additional temporary file for testing file uploads.

    Since temporary files are destroyed as soon as they are closed and fixtures
    are only run once per function by default we need to have a second file
    available for tests that perform multiple uploads.
    """
    return create_temporary_file(fake_file, fake_file_name)


@pytest.fixture
def infected_data_file(infected_file, fake_file_name):
    """Temporary file intended to be marked as infected by ClamAV-REST."""
    return create_temporary_file(infected_file, fake_file_name)


@pytest.fixture
def base_data_file_data(fake_file_name, user):
    """Return data file creation data without a file."""
    return {
        "original_filename": fake_file_name,
        "slug": str(uuid.uuid4()),
        "extension": "txt",
        "section": "Active Case Data",
        "user": str(user.id),
        "quarter": "Q1",
        "year": 2020,
        "stt": int(user.stt.id)
    }


@pytest.fixture
def data_file_data(base_data_file_data, data_file):
    """Return data file creation data."""
    return {
        "file": data_file,
        **base_data_file_data
    }


@pytest.fixture
def other_data_file_data(base_data_file_data, other_data_file):
    """Return data file creation data."""
    return {
        "file": other_data_file,
        **base_data_file_data
    }


@pytest.fixture
def infected_data_file_data(base_data_file_data, infected_data_file):
    """Return data file creation data."""
    return {
        "file": infected_data_file,
        **base_data_file_data
    }


@pytest.fixture
def data_file_instance():
    """Return a data file."""
    return DataFileFactory.create()


@pytest.fixture
def admin():
    """Return a custom LogEntryAdmin."""
    return LogEntryAdmin(LogEntry, AdminSite())
