"""Module testing for data file model."""

from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError

import pytest

from tdpservice.data_files.enums import ProgramCode, SectionName, SubmissionState
from tdpservice.data_files.models import (
    DataFile,
    Program,
    Section,
    ShadowDataFile,
    create_or_update_shadow_data_file,
    get_s3_upload_path,
    get_shadow_s3_upload_path,
)
from tdpservice.data_files.test.factories import (
    DataFileFactory,
    canonical_section_for,
)
from tdpservice.stts.models import STT


def _create_program(code="TEST", slug="test-program", name="Test Program"):
    """Create a test program without conflicting with canonical seed data."""
    return Program.objects.create(code=code, slug=slug, name=name)


@pytest.mark.django_db
def test_program_code_and_string_representation():
    """Programs expose their persisted code and display name."""
    program = _create_program()

    assert program.code == "TEST"
    assert str(program) == "Test Program"


@pytest.mark.django_db
def test_program_code_is_unique():
    """Program codes uniquely identify reporting programs."""
    _create_program()

    with pytest.raises(IntegrityError), transaction.atomic():
        _create_program(slug="another-program", name="Another Program")


@pytest.mark.django_db
def test_section_string_representation():
    """Sections display their program and section names."""
    program = _create_program()
    section = Section.objects.create(program=program, name="Active Case Data")

    assert str(section) == "Test Program - Active Case Data"


@pytest.mark.django_db
def test_section_name_is_unique_per_program():
    """Section names are unique within a program."""
    program = _create_program()
    Section.objects.create(program=program, name="Active Case Data")

    with pytest.raises(IntegrityError), transaction.atomic():
        Section.objects.create(program=program, name="Active Case Data")


@pytest.mark.django_db
def test_data_file_program_comes_from_section(data_file_instance):
    """Data files expose the program associated with their canonical section."""
    program = _create_program()
    section = Section.objects.create(program=program, name="Active Case Data")
    data_file_instance.section = section
    data_file_instance.save(update_fields=["section"])
    data_file_instance.refresh_from_db()

    assert data_file_instance.program == program


def test_data_file_has_required_canonical_section_only():
    """The DataFile classification is a required canonical Section relation."""
    section_field = DataFile._meta.get_field("section")

    assert section_field.null is False
    assert section_field.remote_field.on_delete.__name__ == "PROTECT"
    with pytest.raises(Exception):
        DataFile._meta.get_field("program_type")
    with pytest.raises(Exception):
        DataFile._meta.get_field("section_ref")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "program_type,section_name,is_program_audit",
    [
        (ProgramCode.TANF, SectionName.ACTIVE_CASE_DATA, False),
        (ProgramCode.SSP, SectionName.CLOSED_CASE_DATA, False),
        (ProgramCode.TRIBAL, SectionName.AGGREGATE_DATA, False),
        (
            ProgramCode.FRA,
            SectionName.FRA_WORK_OUTCOME_TANF_EXITERS,
            False,
        ),
        (ProgramCode.TANF, SectionName.ACTIVE_CASE_DATA, True),
        (ProgramCode.TRIBAL, SectionName.ACTIVE_CASE_DATA, True),
    ],
)
def test_new_data_file_resolves_section(
    program_type, section_name, is_program_audit
):
    """Factory inputs resolve to the canonical Section relation."""
    data_file = DataFileFactory.create(
        program_type=program_type,
        section=section_name,
        is_program_audit=is_program_audit,
    )

    assert data_file.section.program.code == program_type
    assert data_file.section.name == section_name
    assert data_file.is_program_audit is is_program_audit


@pytest.mark.django_db
@pytest.mark.parametrize(
    "program_type,section_name,is_program_audit",
    [
        (ProgramCode.TANF, SectionName.ACTIVE_CASE_DATA, False),
        (ProgramCode.SSP, SectionName.CLOSED_CASE_DATA, False),
        (ProgramCode.TRIBAL, SectionName.AGGREGATE_DATA, False),
        (
            ProgramCode.FRA,
            SectionName.FRA_WORK_OUTCOME_TANF_EXITERS,
            False,
        ),
        (ProgramCode.TANF, SectionName.ACTIVE_CASE_DATA, True),
        (ProgramCode.TRIBAL, SectionName.ACTIVE_CASE_DATA, True),
    ],
)
def test_shadow_data_file_projects_canonical_classification(
    program_type, section_name, is_program_audit
):
    """Shadow parser metadata is projected from the production canonical relation."""
    data_file = DataFileFactory.create(
        program_type=program_type,
        section=section_name,
        is_program_audit=is_program_audit,
    )
    shadow = create_or_update_shadow_data_file(data_file)

    assert shadow.program_type == program_type
    assert shadow.section == section_name
    assert shadow.is_program_audit is is_program_audit


@pytest.mark.django_db
def test_shadow_data_file_updates_existing_metadata():
    """Canonical projection refreshes an existing stale shadow row."""
    data_file = DataFileFactory.create()
    shadow = create_or_update_shadow_data_file(data_file)
    ShadowDataFile.objects.filter(pk=shadow.pk).update(
        program_type="STALE", section="Stale Section", is_program_audit=True
    )

    shadow = create_or_update_shadow_data_file(data_file)

    assert shadow.program_type == ProgramCode.TANF
    assert shadow.section == SectionName.ACTIVE_CASE_DATA
    assert shadow.is_program_audit is False


@pytest.mark.django_db
def test_production_and_shadow_upload_paths_use_their_authoritative_metadata():
    """Production and shadow paths preserve text while using separate metadata sources."""
    data_file = DataFileFactory.create()
    shadow = create_or_update_shadow_data_file(data_file)

    expected = (
        f"data_files/{data_file.year}/{data_file.quarter}/{data_file.stt_id}/"
        "TAN/Active Case Data/submission.txt"
    )
    assert get_s3_upload_path(data_file, "submission.txt") == expected
    assert get_shadow_s3_upload_path(shadow, "submission.txt") == expected


def test_shadow_classification_fields_are_explicit_scalars():
    """Shadow classification remains independent of production model fields."""
    assert not ShadowDataFile._meta.get_field("program_type").choices
    assert not ShadowDataFile._meta.get_field("section").choices
    assert (
        ShadowDataFile._meta.get_field("file").upload_to
        is get_shadow_s3_upload_path
    )


@pytest.mark.django_db
def test_create_new_data_file_version(data_file_instance):
    """Test version incrementing logic for data files."""
    new_version = DataFile.create_new_version(
        {
            "year": data_file_instance.year,
            "quarter": data_file_instance.quarter,
            "section": data_file_instance.section,
            "stt": data_file_instance.stt,
            "original_filename": data_file_instance.original_filename,
            "slug": data_file_instance.slug,
            "extension": data_file_instance.extension,
            "user": data_file_instance.user,
            "is_program_audit": data_file_instance.is_program_audit,
        }
    )
    assert new_version.version == data_file_instance.version + 1
    assert new_version.section == data_file_instance.section


@pytest.mark.django_db
def test_find_latest_version(data_file_instance):
    """Test method to find latest version."""
    new_data_file = DataFile.create_new_version(
        {
            "year": data_file_instance.year,
            "quarter": data_file_instance.quarter,
            "section": data_file_instance.section,
            "stt": data_file_instance.stt,
            "original_filename": data_file_instance.original_filename,
            "slug": data_file_instance.slug,
            "extension": data_file_instance.extension,
            "user": data_file_instance.user,
            "is_program_audit": data_file_instance.is_program_audit,
        }
    )

    latest_data_file = DataFile.find_latest_version(
        year=data_file_instance.year,
        quarter=data_file_instance.quarter,
        section=data_file_instance.section,
        stt=data_file_instance.stt.id,
        is_program_audit=data_file_instance.is_program_audit,
    )
    assert latest_data_file.version == new_data_file.version


@pytest.mark.django_db
def test_find_latest_version_number(data_file_instance):
    """Test method to find latest version number."""
    new_data_file = DataFile.create_new_version(
        {
            "year": data_file_instance.year,
            "quarter": data_file_instance.quarter,
            "section": data_file_instance.section,
            "stt": data_file_instance.stt,
            "original_filename": data_file_instance.original_filename,
            "slug": data_file_instance.slug,
            "extension": data_file_instance.extension,
            "user": data_file_instance.user,
            "is_program_audit": data_file_instance.is_program_audit,
        }
    )

    latest_version = DataFile.find_latest_version_number(
        year=data_file_instance.year,
        quarter=data_file_instance.quarter,
        section=data_file_instance.section,
        stt=data_file_instance.stt.id,
        is_program_audit=data_file_instance.is_program_audit,
    )
    assert latest_version == new_data_file.version


@pytest.mark.django_db
def test_latest_version_uses_canonical_section(data_file_instance):
    """Canonical Section identity defines a version family."""
    latest = DataFileFactory(
        stt=data_file_instance.stt,
        year=data_file_instance.year,
        quarter=data_file_instance.quarter,
        section=data_file_instance.section,
        is_program_audit=data_file_instance.is_program_audit,
        version=data_file_instance.version + 1,
    )

    assert DataFile.find_latest_version_number(
        year=data_file_instance.year,
        quarter=data_file_instance.quarter,
        section=data_file_instance.section,
        stt=data_file_instance.stt,
        is_program_audit=False,
    ) == latest.version


@pytest.mark.django_db
def test_standard_and_program_audit_files_have_separate_version_families(
    data_file_instance,
):
    """PIA classification remains part of canonical version identity."""
    audit_file = DataFileFactory(
        stt=data_file_instance.stt,
        year=data_file_instance.year,
        quarter=data_file_instance.quarter,
        section=data_file_instance.section,
        is_program_audit=True,
    )

    new_standard = DataFile.create_new_version(
        {
            "year": data_file_instance.year,
            "quarter": data_file_instance.quarter,
            "section": data_file_instance.section,
            "stt": data_file_instance.stt,
            "user": data_file_instance.user,
            "is_program_audit": False,
        }
    )

    assert new_standard.version == data_file_instance.version + 1
    assert audit_file.version == 1
    assert DataFile.find_latest_version_number(
        year=data_file_instance.year,
        quarter=data_file_instance.quarter,
        section=data_file_instance.section,
        stt=data_file_instance.stt,
        is_program_audit=True,
    ) == 1


@pytest.mark.django_db
def test_data_file_protects_canonical_section_from_deletion(data_file_instance):
    """A Section cannot be deleted while a DataFile canonically references it."""
    with pytest.raises(ProtectedError):
        data_file_instance.section.delete()


@pytest.mark.django_db
def test_data_file_protects_canonical_program_from_deletion(data_file_instance):
    """A Program cannot cascade-delete a Section referenced by a DataFile."""
    with pytest.raises(ProtectedError):
        data_file_instance.program.delete()


@pytest.mark.django_db
@pytest.mark.parametrize("is_program_audit", [False, True])
def test_data_file_canonical_version_identity_is_unique(
    data_file_instance, is_program_audit
):
    """Standard and PIA files each enforce canonical version uniqueness."""
    data_file_instance.is_program_audit = is_program_audit
    data_file_instance.save(update_fields=["is_program_audit"])

    with pytest.raises(IntegrityError), transaction.atomic():
        DataFileFactory.create(
            section=data_file_instance.section,
            stt=data_file_instance.stt,
            year=data_file_instance.year,
            quarter=data_file_instance.quarter,
            version=data_file_instance.version,
            is_program_audit=is_program_audit,
        )


@pytest.mark.django_db
def test_data_files_filename_is_expected(user):
    """Test that the file name matches the file name expected based on the stt of each data file."""
    all_stts = STT.objects.all()

    if all_stts.count == 0:
        raise Exception("There are no stts, the test is invalid.")
    for stt in all_stts.iterator():
        for section in stt.filenames:
            new_data_file = DataFile.create_new_version(
                {
                    "year": 2020,
                    "quarter": "Q1",
                    "section": section,
                    "user": user,
                    "stt": stt,
                    "is_program_audit": False,
                }
            )
            assert new_data_file.filename == stt.filenames[section]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "program_type, filenames, expected_filename",
    [
        (
            ProgramCode.SSP,
            {"Active Case Data": "section-based-ssp.txt"},
            "section-based-ssp.txt",
        ),
        (
            ProgramCode.TRIBAL,
            {"Active Case Data": "section-based-tribal.txt"},
            "section-based-tribal.txt",
        ),
        (
            ProgramCode.SSP,
            {"SSP Active Case Data": "legacy-ssp.txt"},
            "legacy-ssp.txt",
        ),
        (
            ProgramCode.TRIBAL,
            {"Tribal Active Case Data": "legacy-tribal.txt"},
            "legacy-tribal.txt",
        ),
    ],
)
def test_data_files_filename_prefers_section_key_with_legacy_fallback(
    user, program_type, filenames, expected_filename
):
    """File name lookup supports section keys and legacy prefixed keys."""
    stt = STT.objects.create(
        name=f"Filename Lookup {program_type} {expected_filename}",
        filenames=filenames,
    )
    data_file = DataFile.create_new_version(
        {
            "year": 2020,
            "quarter": "Q1",
            "section": canonical_section_for(
                program_type,
                "Active Case Data",
            ),
            "user": user,
            "stt": stt,
            "is_program_audit": False,
        }
    )

    assert data_file.filename == expected_filename


@pytest.mark.django_db
@pytest.mark.parametrize(
    "section, program_type",
    [
        ("Closed Case Data", "TRIBAL"),
        ("Active Case Data", "TRIBAL"),
        ("Aggregate Data", "SSP"),
        ("Closed Case Data", "SSP"),
        ("Active Case Data", "TAN"),
        ("Aggregate Data", "TAN"),
        ("Work Outcomes of TANF Exiters", "FRA"),
        ("Secondary School Attainment", "FRA"),
        ("Supplemental Work Outcomes", "FRA"),
    ],
)
def test_program_comes_from_section(
    base_data_file_data, data_analyst, stt, section, program_type
):
    """The canonical section supplies the DataFile program."""
    df = DataFile.create_new_version(
        {
            "year": base_data_file_data["year"],
            "quarter": base_data_file_data["quarter"],
            "section": canonical_section_for(program_type, section),
            "stt": stt,
            "original_filename": base_data_file_data["original_filename"],
            "slug": base_data_file_data["slug"],
            "extension": base_data_file_data["extension"],
            "user": data_analyst,
            "is_program_audit": False,
        }
    )

    assert df.section.name == section
    assert df.section.program.code == program_type


@pytest.mark.django_db
def test_fiscal_year(data_file_instance):
    """Test property fiscal_year."""
    df = DataFile.create_new_version(
        {
            "year": data_file_instance.year,
            "quarter": data_file_instance.quarter,
            "section": data_file_instance.section,
            "stt": data_file_instance.stt,
            "original_filename": data_file_instance.original_filename,
            "slug": data_file_instance.slug,
            "extension": data_file_instance.extension,
            "user": data_file_instance.user,
            "is_program_audit": False,
        }
    )

    assert df.fiscal_year == "2020 - Q1 (Oct - Dec)"
    df.quarter = "Q2"
    assert df.fiscal_year == "2020 - Q2 (Jan - Mar)"
    df.quarter = "Q3"
    assert df.fiscal_year == "2020 - Q3 (Apr - Jun)"
    df.quarter = "Q4"
    assert df.fiscal_year == "2020 - Q4 (Jul - Sep)"


@pytest.mark.django_db
def test_data_file_defaults_to_uploaded_submission_state(data_file_instance):
    """Test new data files default to the uploaded submission state."""
    df = DataFile.create_new_version(
        {
            "year": data_file_instance.year,
            "quarter": data_file_instance.quarter,
            "section": data_file_instance.section,
            "stt": data_file_instance.stt,
            "original_filename": data_file_instance.original_filename,
            "slug": data_file_instance.slug,
            "extension": data_file_instance.extension,
            "user": data_file_instance.user,
            "is_program_audit": data_file_instance.is_program_audit,
        }
    )

    assert df.state == SubmissionState.UPLOADED


def test_submission_state_enum_matches_parsing_refactor_writeup():
    """Test the durable submission lifecycle states are defined on the enum."""
    assert list(SubmissionState.values) == [
        "uploaded",
        "virus_scan_started",
        "virus_scan_failed",
        "virus_scan_completed",
        "reparse_requested",
        "parse_started",
        "parse_failed",
        "parsed_with_errors",
        "parse_completed",
        "stuck",
        "completed",
        "canceled",
    ]
