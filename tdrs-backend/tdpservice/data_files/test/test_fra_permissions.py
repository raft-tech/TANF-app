"""FRA API access requires permission in addition to existing role and scope rules."""

import io

from django.contrib.auth.models import Permission
from django.core.files.base import ContentFile
from django.core.files.storage import InMemoryStorage
from django.http.response import HttpResponseBase

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from tdpservice.data_files.models import DataFile, Program, Section
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.parsers.models import DataFileSummary
from tdpservice.parsers.test.factories import DataFileSummaryFactory
from tdpservice.users.models import AccountApprovalStatusChoices, User

pytestmark = pytest.mark.django_db

READ_ACTIONS = ["list", "retrieve", "download", "download_error_report", "logs"]
FRA_SECTIONS = [
    Section.Name.FRA_WORK_OUTCOMES,
    Section.Name.FRA_SECONDARY_SCHOOL_ATTAINMENT,
    Section.Name.FRA_SUPPLEMENTAL_WORK_OUTCOMES,
]


@pytest.fixture(autouse=True)
def local_file_storage(mocker) -> None:
    """Keep file and log downloads independent of external storage."""
    storage = InMemoryStorage()
    mocker.patch.object(DataFile._meta.get_field("file"), "storage", storage)
    mocker.patch.object(
        DataFileSummary._meta.get_field("error_report"), "storage", storage
    )
    mocker.patch(
        "tdpservice.data_files.views.S3FileHandler.download_file",
        side_effect=lambda **kwargs: io.BytesIO(b"parser log"),
    )


def set_fra_access(user: User, allowed: bool) -> User:
    """Set effective FRA access, including permissions inherited from groups."""
    permission = Permission.objects.get(codename="has_fra_access")
    user.user_permissions.remove(permission)
    for group in user.groups.all():
        group.permissions.remove(permission)
    if allowed:
        user.user_permissions.add(permission)
    return User.objects.get(pk=user.pk)


def create_file(user: User, section: str, program: str) -> DataFile:
    """Create a downloadable submission with a cached error report."""
    datafile = DataFileFactory.create(
        user=user,
        stt=user.stt,
        section=section,
        program_type=program,
        s3_versioning_id=None,
    )
    DataFileSummaryFactory.create(
        datafile=datafile,
        error_report=ContentFile(b"error report", name="report.xlsx"),
    )
    return datafile


def read_file(client: APIClient, datafile: DataFile, action: str) -> HttpResponseBase:
    """Request a submission through each public read endpoint."""
    if action == "list":
        file_type = "tanf"
        if datafile.program.code == Program.Code.FRA:
            file_type = datafile.section.name
        elif datafile.program.code == Program.Code.SSP:
            file_type = "ssp-moe"
        return client.get(
            "/v1/data_files/",
            {"stt": datafile.stt_id, "file_type": file_type},
        )
    suffix = "" if action == "retrieve" else f"{action}/"
    return client.get(f"/v1/data_files/{datafile.pk}/{suffix}")


@pytest.mark.parametrize("section", FRA_SECTIONS)
@pytest.mark.parametrize("action", READ_ACTIONS)
@pytest.mark.parametrize("allowed", [False, True])
def test_fra_reads_require_permission(
    api_client, data_analyst, section: str, action: str, allowed: bool
) -> None:
    """Same-STT FRA reads require explicit access for every FRA section."""
    data_analyst = set_fra_access(data_analyst, allowed)
    datafile = create_file(data_analyst, section, Program.Code.FRA)
    api_client.force_authenticate(user=data_analyst)

    response = read_file(api_client, datafile, action)

    expected = status.HTTP_200_OK if allowed else status.HTTP_403_FORBIDDEN
    assert response.status_code == expected
    if allowed and action == "list":
        assert [record["id"] for record in response.data] == [datafile.pk]


@pytest.mark.parametrize("action", READ_ACTIONS)
def test_fra_reads_allow_group_permission(
    api_client, data_analyst, action: str
) -> None:
    """FRA access inherited from a role authorizes the same read endpoints."""
    data_analyst = set_fra_access(data_analyst, False)
    data_analyst.groups.get().permissions.add(
        Permission.objects.get(codename="has_fra_access")
    )
    datafile = create_file(
        data_analyst, Section.Name.FRA_WORK_OUTCOMES, Program.Code.FRA
    )
    api_client.force_authenticate(user=data_analyst)

    assert read_file(api_client, datafile, action).status_code == status.HTTP_200_OK


@pytest.mark.parametrize("action", READ_ACTIONS)
def test_fra_reads_allow_system_admin_without_fra_permission(
    api_client, ofa_system_admin, data_analyst, action: str
) -> None:
    """System administrators retain the exception used by FRA upload validation."""
    ofa_system_admin = set_fra_access(ofa_system_admin, False)
    assert not ofa_system_admin.has_fra_access
    datafile = create_file(
        data_analyst, Section.Name.FRA_WORK_OUTCOMES, Program.Code.FRA
    )
    api_client.force_authenticate(user=ofa_system_admin)

    assert read_file(api_client, datafile, action).status_code == status.HTTP_200_OK


@pytest.mark.parametrize("action", READ_ACTIONS)
@pytest.mark.parametrize("allowed", [False, True])
def test_regional_fra_reads_preserve_download_restriction(
    api_client, regional_user, data_analyst, action: str, allowed: bool
) -> None:
    """Regional users need FRA access and still cannot download original files."""
    regional_user = set_fra_access(regional_user, allowed)
    datafile = create_file(
        data_analyst, Section.Name.FRA_WORK_OUTCOMES, Program.Code.FRA
    )
    api_client.force_authenticate(user=regional_user)

    expected = (
        status.HTTP_200_OK
        if allowed and action != "download"
        else status.HTTP_403_FORBIDDEN
    )
    assert read_file(api_client, datafile, action).status_code == expected


@pytest.mark.parametrize("action", READ_ACTIONS)
@pytest.mark.parametrize("role", ["data_analyst", "regional_user"])
def test_fra_access_does_not_override_location_scope(
    request, api_client, other_stt, role: str, action: str
) -> None:
    """FRA permission cannot grant access outside the user's STT or region."""
    user = set_fra_access(request.getfixturevalue(role), True)
    datafile = DataFileFactory.create(
        stt=other_stt,
        section=Section.Name.FRA_WORK_OUTCOMES,
        program_type=Program.Code.FRA,
    )
    api_client.force_authenticate(user=user)

    response = read_file(api_client, datafile, action)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize("action", READ_ACTIONS)
@pytest.mark.parametrize("program", [Program.Code.TANF, Program.Code.SSP])
def test_non_fra_reads_do_not_require_fra_access(
    api_client, data_analyst, program: str, action: str
) -> None:
    """Existing TANF and SSP reads remain available without FRA permission."""
    data_analyst = set_fra_access(data_analyst, False)
    datafile = create_file(data_analyst, Section.Name.ACTIVE_CASE_DATA, program)
    api_client.force_authenticate(user=data_analyst)

    assert read_file(api_client, datafile, action).status_code == status.HTTP_200_OK


@pytest.mark.parametrize("action", READ_ACTIONS)
def test_fra_access_does_not_override_approval(
    api_client, data_analyst, action: str
) -> None:
    """FRA permission does not authorize an unapproved user."""
    data_analyst = set_fra_access(data_analyst, True)
    data_analyst.account_approval_status = AccountApprovalStatusChoices.INITIAL
    data_analyst.save()
    datafile = create_file(
        data_analyst, Section.Name.FRA_WORK_OUTCOMES, Program.Code.FRA
    )
    api_client.force_authenticate(user=data_analyst)

    assert (
        read_file(api_client, datafile, action).status_code == status.HTTP_403_FORBIDDEN
    )


@pytest.mark.parametrize("action", READ_ACTIONS)
def test_fra_access_does_not_override_model_permissions(
    api_client, data_analyst, action: str
) -> None:
    """FRA permission alone does not grant the ability to view data files."""
    data_analyst = set_fra_access(data_analyst, True)
    permission = Permission.objects.get(
        content_type__app_label="data_files", codename="view_datafile"
    )
    for group in data_analyst.groups.all():
        group.permissions.remove(permission)
    data_analyst.user_permissions.remove(permission)
    datafile = create_file(
        data_analyst, Section.Name.FRA_WORK_OUTCOMES, Program.Code.FRA
    )
    api_client.force_authenticate(user=data_analyst)

    assert (
        read_file(api_client, datafile, action).status_code == status.HTTP_403_FORBIDDEN
    )
