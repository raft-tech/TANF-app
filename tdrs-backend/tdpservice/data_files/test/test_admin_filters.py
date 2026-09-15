"""Tests for admin list filters on DataFiles."""

import pytest
from django.contrib import admin
from django.test import RequestFactory

from tdpservice.data_files.admin.admin import DataFileAdmin
from tdpservice.data_files.admin.filters import LatestReparseEvent, VersionFilter
from tdpservice.data_files.models import DataFile, Section
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.stts.test.factories import STTFactory


class DummyChangeList:
    """Minimal changelist stub for filter choice testing."""

    def get_query_string(self, new_params, remove):
        """Return a simplified query string."""
        return "&".join([f"{key}={value}" for key, value in new_params.items()])


@pytest.mark.django_db
def test_latest_reparse_event_lookups_and_choices():
    """Return lookups and selection states for latest reparse filter."""
    request = RequestFactory().get(
        "/", {LatestReparseEvent.parameter_name: "latest"}
    )
    model_admin = admin.ModelAdmin(DataFile, admin.site)

    filter_instance = LatestReparseEvent(
        request,
        request.GET.dict(),
        DataFile,
        model_admin,
    )
    filter_instance.used_parameters[filter_instance.parameter_name] = "latest"

    assert filter_instance.lookups(request, model_admin) == (
        (None, "All"),
        ("latest", "Latest"),
    )

    choices = list(filter_instance.choices(DummyChangeList()))
    selected = {choice["display"]: choice["selected"] for choice in choices}
    assert selected["Latest"] is True
    assert selected["All"] is False


@pytest.mark.django_db
def test_latest_reparse_event_queryset_filters_latest(stt):
    """Filter datafiles to latest reparse event when selected."""
    request = RequestFactory().get("/")
    model_admin = admin.ModelAdmin(DataFile, admin.site)

    filter_instance = LatestReparseEvent(
        request,
        {LatestReparseEvent.parameter_name: "latest"},
        DataFile,
        model_admin,
    )

    meta_old = ReparseMeta.objects.create(db_backup_location="s3://old")
    meta_new = ReparseMeta.objects.create(db_backup_location="s3://new")

    old_file = DataFileFactory(stt=stt, version=1)
    new_file = DataFileFactory(stt=stt, version=2)
    old_file.reparses.add(meta_old)
    new_file.reparses.add(meta_new)

    filtered = filter_instance.queryset(request, DataFile.objects.all())

    assert set(filtered.values_list("id", flat=True)) == {new_file.id}


@pytest.mark.django_db
def test_latest_reparse_event_queryset_no_latest_returns_all(monkeypatch):
    """Return unfiltered queryset when latest meta is missing."""
    request = RequestFactory().get("/")
    model_admin = admin.ModelAdmin(DataFile, admin.site)

    filter_instance = LatestReparseEvent(
        request,
        {LatestReparseEvent.parameter_name: "latest"},
        DataFile,
        model_admin,
    )

    monkeypatch.setattr(ReparseMeta, "get_latest", staticmethod(lambda: None))

    datafile = DataFileFactory()
    queryset = DataFile.objects.all()

    assert set(filter_instance.queryset(request, queryset)) == {datafile}


@pytest.mark.django_db
def test_latest_reparse_event_queryset_no_value_returns_all():
    """Return unfiltered queryset when filter value is not set."""
    request = RequestFactory().get("/")
    model_admin = admin.ModelAdmin(DataFile, admin.site)

    filter_instance = LatestReparseEvent(
        request,
        {},
        DataFile,
        model_admin,
    )

    datafile = DataFileFactory()
    queryset = DataFile.objects.all()

    assert set(filter_instance.queryset(request, queryset)) == {datafile}


@pytest.mark.django_db
def test_latest_reparse_event_queryset_empty_is_noop():
    """Keep empty queryset unchanged."""
    request = RequestFactory().get("/")
    model_admin = admin.ModelAdmin(DataFile, admin.site)

    filter_instance = LatestReparseEvent(
        request,
        {LatestReparseEvent.parameter_name: "latest"},
        DataFile,
        model_admin,
    )

    queryset = DataFile.objects.none()
    assert list(filter_instance.queryset(request, queryset)) == []


@pytest.mark.django_db
def test_version_filter_returns_latest_versions():
    """Return only latest versions per file group."""
    request = RequestFactory().get("/")
    model_admin = admin.ModelAdmin(DataFile, admin.site)

    stt = STTFactory()
    base_kwargs = {
        "stt": stt,
        "year": 2022,
        "quarter": "Q1",
        "is_program_audit": False,
    }
    old_version = DataFileFactory(version=1, **base_kwargs)
    new_version = DataFileFactory(version=2, **base_kwargs)
    other_group = DataFileFactory(
        version=1,
        stt=stt,
        year=2022,
        quarter="Q2",
        is_program_audit=False,
    )

    filter_instance = VersionFilter(request, {}, DataFile, model_admin)
    filtered = filter_instance.queryset(request, DataFile.objects.all())

    assert set(filtered.values_list("id", flat=True)) == {
        new_version.id,
        other_group.id,
    }
    assert old_version.id not in filtered.values_list("id", flat=True)


@pytest.mark.django_db
def test_version_filter_ignores_legacy_classification_drift(stt):
    """Latest-version grouping follows the canonical Section relationship."""
    old_version = DataFileFactory(stt=stt, version=1)
    new_version = DataFileFactory(
        stt=stt,
        version=2,
        section_ref=old_version.section_ref,
    )
    DataFile.objects.filter(pk=old_version.pk).update(
        program_type=DataFile.ProgramType.FRA,
        section=DataFile.Section.FRA_WORK_OUTCOME_TANF_EXITERS,
    )
    request = RequestFactory().get("/")
    filter_instance = VersionFilter(
        request,
        {},
        DataFile,
        admin.ModelAdmin(DataFile, admin.site),
    )

    filtered = filter_instance.queryset(request, DataFile.objects.all())

    assert list(filtered) == [new_version]


@pytest.mark.django_db
def test_fra_filter_uses_canonical_program(stt):
    """FRA admin filtering ignores transitional classification drift."""
    fra_section = Section.from_legacy_values(
        DataFile.ProgramType.FRA,
        DataFile.Section.FRA_WORK_OUTCOME_TANF_EXITERS,
    )
    fra_file = DataFileFactory(stt=stt, section_ref=fra_section)
    tanf_file = DataFileFactory(stt=stt)
    DataFile.objects.filter(pk=fra_file.pk).update(
        program_type=DataFile.ProgramType.TANF,
        section=DataFile.Section.CLOSED_CASE_DATA,
    )
    request = RequestFactory().get("/", {"fra_access": "1"})
    filter_instance = DataFileAdmin.FRA_AccessFilter(
        request,
        request.GET.copy(),
        DataFile,
        DataFileAdmin(DataFile, admin.site),
    )

    filtered = filter_instance.queryset(request, DataFile.objects.all())

    assert list(filtered) == [fra_file]
    assert tanf_file not in filtered


@pytest.mark.django_db
def test_program_and_section_admin_filters_use_canonical_relations(stt):
    """Admin classification filters retain scalar values but query canonical data."""
    ssp_section = Section.from_legacy_values(
        DataFile.ProgramType.SSP,
        DataFile.Section.CLOSED_CASE_DATA,
    )
    ssp_file = DataFileFactory(stt=stt, section_ref=ssp_section)
    DataFile.objects.filter(pk=ssp_file.pk).update(
        program_type=DataFile.ProgramType.TANF,
        section=DataFile.Section.ACTIVE_CASE_DATA,
    )
    model_admin = DataFileAdmin(DataFile, admin.site)

    program_request = RequestFactory().get("/", {"program_type__exact": "SSP"})
    program_filter = DataFileAdmin.ProgramTypeFilter(
        program_request,
        program_request.GET.copy(),
        DataFile,
        model_admin,
    )
    section_request = RequestFactory().get(
        "/",
        {"section__exact": DataFile.Section.CLOSED_CASE_DATA},
    )
    section_filter = DataFileAdmin.SectionFilter(
        section_request,
        section_request.GET.copy(),
        DataFile,
        model_admin,
    )

    assert list(program_filter.queryset(program_request, DataFile.objects.all())) == [
        ssp_file
    ]
    assert list(section_filter.queryset(section_request, DataFile.objects.all())) == [
        ssp_file
    ]


@pytest.mark.django_db
def test_version_filter_with_value_returns_unfiltered(stt):
    """Return unfiltered queryset when filter has a value."""
    request = RequestFactory().get("/")
    model_admin = admin.ModelAdmin(DataFile, admin.site)

    datafile = DataFileFactory(stt=stt)
    other_file = DataFileFactory(stt=stt, version=2)
    queryset = DataFile.objects.all()

    filter_instance = VersionFilter(
        request,
        {VersionFilter.parameter_name: "1"},
        DataFile,
        model_admin,
    )

    assert set(filter_instance.queryset(request, queryset)) == {datafile, other_file}


@pytest.mark.django_db
def test_version_filter_empty_queryset_is_noop():
    """Keep empty queryset unchanged for version filter."""
    request = RequestFactory().get("/")
    model_admin = admin.ModelAdmin(DataFile, admin.site)

    filter_instance = VersionFilter(request, {}, DataFile, model_admin)

    assert list(filter_instance.queryset(request, DataFile.objects.none())) == []
