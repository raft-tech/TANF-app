"""Globally available pytest fixtures."""
import pytest
from rest_framework.test import APIClient

from tdpservice.users.test.factories import UserFactory
from tdpservice.stts.test.factories import STTFactory, RegionFactory
from django.contrib.auth.models import Group


@pytest.fixture(scope="function")
def api_client():
    """Return an API client for testing."""
    return APIClient()


@pytest.fixture
def user():
    """Return a basic, non-admin user."""
    return UserFactory.create()


@pytest.fixture
def ofa_admin():
    """Return an ofa admin user."""
    return UserFactory.create(groups=(Group.objects.get(name="OFA Admin"),))


@pytest.fixture
def ofa_analyst():
    """Return an OFA Analyst user."""
    return UserFactory.create(groups=(Group.objects.get(name="OFA Analyst"),))


@pytest.fixture
def data_prepper():
    """Return a data prepper user."""
    return UserFactory.create(groups=(Group.objects.get(name="Data Prepper"),))


@pytest.fixture
def stt():
    """Return an STT."""
    return STTFactory.create()


@pytest.fixture
def region():
    """Return a region."""
    return RegionFactory.create()
