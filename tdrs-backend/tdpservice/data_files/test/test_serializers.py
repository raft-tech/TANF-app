"""Test data file serializers."""

from django.core.exceptions import ValidationError

import pytest

from tdpservice.data_files.errors import ImmutabilityError
from tdpservice.data_files.models import DataFile
from tdpservice.data_files.serializers import DataFileSerializer
from tdpservice.data_files.validators import (
    validate_file_extension,
    validate_file_infection,
)
from tdpservice.security.clients import ClamAVClient
from tdpservice.stts.models import STT


@pytest.mark.django_db
def test_serializer_with_valid_data(data_file_data, data_analyst):
    """If a serializer has valid data it will return a valid object."""
    create_serializer = DataFileSerializer(
        context={"user": data_analyst}, data=data_file_data
    )
    create_serializer.is_valid(raise_exception=True)
    assert create_serializer.is_valid() is True


@pytest.mark.django_db
def test_serializer_increment_create(data_file_data, other_data_file_data, user):
    """Test serializer produces data_files with correct version."""
    serializer_1 = DataFileSerializer(context={"user": user}, data=data_file_data)
    assert serializer_1.is_valid() is True
    data_file_1 = serializer_1.save()

    serializer_2 = DataFileSerializer(context={"user": user}, data=other_data_file_data)
    assert serializer_2.is_valid() is True
    data_file_2 = serializer_2.save()

    assert data_file_2.version == data_file_1.version + 1
    assert data_file_1.section_ref.program.code == data_file_1.program_type
    assert data_file_1.section_ref.name == data_file_1.section
    assert data_file_2.section_ref == data_file_1.section_ref


@pytest.mark.django_db
@pytest.mark.parametrize(
    "program_type,section_name,ssp,stt_type,is_program_audit",
    [
        (
            DataFile.ProgramType.TANF,
            DataFile.Section.ACTIVE_CASE_DATA,
            False,
            "state",
            False,
        ),
        (
            DataFile.ProgramType.SSP,
            DataFile.Section.CLOSED_CASE_DATA,
            True,
            "state",
            False,
        ),
        (
            DataFile.ProgramType.TRIBAL,
            DataFile.Section.AGGREGATE_DATA,
            False,
            "tribe",
            False,
        ),
        (
            DataFile.ProgramType.FRA,
            DataFile.Section.FRA_WORK_OUTCOME_TANF_EXITERS,
            False,
            "state",
            False,
        ),
        (
            DataFile.ProgramType.TANF,
            DataFile.Section.ACTIVE_CASE_DATA,
            False,
            "state",
            True,
        ),
        (
            DataFile.ProgramType.TRIBAL,
            DataFile.Section.ACTIVE_CASE_DATA,
            False,
            "tribe",
            True,
        ),
    ],
)
def test_serializer_creates_canonically_consistent_data_files(
    data_file_data,
    ofa_system_admin,
    program_type,
    section_name,
    ssp,
    stt_type,
    is_program_audit,
):
    """Compatibility inputs produce canonical values for every supported class."""
    data_file_data["section"] = section_name
    data_file_data["ssp"] = ssp
    data_file_data["is_program_audit"] = is_program_audit
    if program_type == DataFile.ProgramType.FRA:
        data_file_data["file"].name = "report.csv"
        data_file_data["original_filename"] = "report.csv"
        data_file_data["extension"] = "csv"
    stt = STT.objects.get(pk=data_file_data["stt"])
    stt.type = stt_type
    stt.save(update_fields=["type"])
    data_file_data["user"] = ofa_system_admin.id
    serializer = DataFileSerializer(
        context={"user": ofa_system_admin}, data=data_file_data
    )

    serializer.is_valid(raise_exception=True)
    data_file = serializer.save()

    assert data_file.section_ref.program.code == program_type
    assert data_file.section_ref.name == section_name
    assert data_file.program_type == program_type
    assert data_file.section == section_name
    assert data_file.is_program_audit is is_program_audit


@pytest.mark.django_db
def test_serializer_rejects_ssp_program_audit(data_file_data, data_analyst):
    """SSP compatibility input cannot create a Program Integrity Audit file."""
    data_file_data["ssp"] = True
    data_file_data["is_program_audit"] = True
    serializer = DataFileSerializer(
        context={"user": data_analyst}, data=data_file_data
    )

    assert serializer.is_valid() is False
    assert "is_program_audit" in serializer.errors


@pytest.mark.django_db
def test_serializer_rejects_fra_program_audit(csv_data_file, ofa_system_admin):
    """FRA compatibility input cannot create a Program Integrity Audit file."""
    csv_data_file["is_program_audit"] = True
    serializer = DataFileSerializer(
        context={"user": ofa_system_admin}, data=csv_data_file
    )

    assert serializer.is_valid() is False
    assert "is_program_audit" in serializer.errors


@pytest.mark.django_db
def test_serializer_rejects_section_for_derived_program(
    csv_data_file, ofa_system_admin
):
    """Compatibility inputs must resolve to one canonical Program/Section pair."""
    csv_data_file["ssp"] = True
    serializer = DataFileSerializer(
        context={"user": ofa_system_admin}, data=csv_data_file
    )

    assert serializer.is_valid() is False
    assert "section" in serializer.errors


@pytest.mark.django_db
def test_immutability_of_data_file(data_file_instance):
    """Test that data file can only be created."""
    with pytest.raises(ImmutabilityError):
        serializer = DataFileSerializer(
            data_file_instance,
            data={
                "original_filename": "BadGuy.js",
            },
            partial=True,
        )

        serializer.is_valid()
        serializer.save()


@pytest.mark.django_db
def test_created_at(data_file_data, data_analyst):
    """Test that serializer creates a DataFile with a created_at timestamp."""
    create_serializer = DataFileSerializer(
        context={"user": data_analyst}, data=data_file_data
    )
    assert create_serializer.is_valid() is True
    data_file = create_serializer.save()

    assert data_file.created_at


@pytest.mark.django_db
def test_state_not_exposed_by_serializer(data_file_instance):
    """Test submission state remains schema-only for serializer output."""
    serialized = DataFileSerializer(data_file_instance).data

    assert "state" not in serialized


@pytest.mark.parametrize(
    "file_name",
    [
        "sample.txt",
        "Sample",
        "ADS.E2J.FTP4.TS06.txt",
        "ADS.E2J.FTP4.TS06",
        "ADS.E2J.FTP2.MS18",
        "ADS.E2J.FTP1.TS278",
    ],
)
def test_accepts_valid_file_extensions(file_name):
    """Test valid file names are accepted by serializer validation."""
    try:
        validate_file_extension(file_name)
    except ValidationError as err:
        pytest.fail(f"Received unexpected error: {err}")


@pytest.mark.parametrize(
    "file_name",
    [
        "java.jar",
        "mysql.bin",
        "malicious.exe",
        "exec.py",
        "hax.pdf",
        "types.ts",
        "notepad.txt.exe",
        "ADS.E2J.FTP1.TS273894",
        "ADS.E2J.FTP1.TS38WRONG",
        "ADS.E2J.FTP1.MS38483",
        "ADS.E2J.FTP1.MS38WRONG",
    ],
)
def test_rejects_invalid_file_extensions(file_name):
    """Test invalid file names are rejected by serializer validation."""
    with pytest.raises(ValidationError):
        validate_file_extension(file_name)


@pytest.mark.django_db
def test_rejects_infected_file(infected_file, fake_file_name, user, settings):
    """Test infected files are rejected by the AV validator helper."""
    settings.CLAMAV_NEEDED = True
    with pytest.raises(ValidationError):
        validate_file_infection(infected_file, fake_file_name, user)


@pytest.mark.django_db
def test_rejects_uploads_on_clamav_connection_error(
    fake_file, fake_file_name, mocker, user, settings
):
    """Test that the AV validator helper rejects if ClamAV is down."""
    settings.CLAMAV_NEEDED = True
    mocker.patch(
        "tdpservice.security.clients.ClamAVClient.scan_file",
        side_effect=ClamAVClient.ServiceUnavailable(),
    )
    with pytest.raises(ValidationError):
        validate_file_infection(fake_file, fake_file_name, user)
