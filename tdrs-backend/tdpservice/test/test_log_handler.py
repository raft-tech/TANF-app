"""Tests for S3FileHandler log cleanup behavior."""

import os
import tempfile

import pytest
from botocore.exceptions import ClientError

from tdpservice.data_files.models import DataFile, create_or_update_shadow_data_file
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.data_files.util import (
    create_legacy_s3_log_file_path,
    create_s3_log_file_path,
)
from tdpservice.log_handler import S3FileHandler


@pytest.fixture
def mock_datafile(mocker):
    """Return a mock DataFile-like object with required attributes."""
    df = mocker.MagicMock()
    df.year = 2024
    df.quarter = "Q1"
    df.stt = "test_stt"
    df.program_type = "TAN"
    df.section = "Active Case Data"
    df.id = 99
    return df


@pytest.fixture
def handler(mocker):
    """Return an S3FileHandler with a real temp file and a mocked S3 client."""
    mocker.patch("tdpservice.log_handler.boto3.client")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as f:
        tmp_path = f.name

    h = S3FileHandler(filename=tmp_path)
    yield h

    # Cleanup in case a test leaves the file behind unexpectedly
    if os.path.exists(tmp_path):
        os.remove(tmp_path)


def test_doRollover_removes_local_file_after_successful_upload(handler, mock_datafile):
    """Local log file is deleted from disk after a successful S3 upload."""
    handler.s3_client.upload_file.return_value = None

    assert os.path.exists(handler.filename)
    log_path = handler.filename

    handler.doRollover(mock_datafile)

    assert not os.path.exists(log_path)


def test_doRollover_removes_local_file_after_failed_upload(handler, mock_datafile):
    """Local log file is deleted from disk even when the S3 upload fails."""
    handler.s3_client.upload_file.side_effect = ClientError(
        {"Error": {"Code": "NoSuchBucket", "Message": "bucket not found"}},
        "upload_file",
    )

    assert os.path.exists(handler.filename)
    log_path = handler.filename

    handler.doRollover(mock_datafile)

    assert not os.path.exists(log_path)


def test_doRollover_uploads_to_s3_before_deleting(handler, mock_datafile):
    """S3 upload is attempted before the local file is removed."""
    upload_called_with_file_present = []

    def track_upload(**kwargs):
        upload_called_with_file_present.append(os.path.exists(kwargs["Filename"]))

    handler.s3_client.upload_file.side_effect = lambda **kwargs: track_upload(**kwargs)

    handler.doRollover(mock_datafile)

    assert upload_called_with_file_present == [True]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "program_type,section_name,legacy_suffix",
    [
        ("TAN", DataFile.Section.ACTIVE_CASE_DATA, "Active Case Data"),
        ("SSP", DataFile.Section.ACTIVE_CASE_DATA, "SSP Active Case Data"),
        ("TRIBAL", DataFile.Section.ACTIVE_CASE_DATA, "Tribal Active Case Data"),
        (
            "FRA",
            DataFile.Section.FRA_WORK_OUTCOME_TANF_EXITERS,
            "Work Outcomes of TANF Exiters",
        ),
    ],
)
def test_log_paths_use_canonical_production_metadata(
    program_type, section_name, legacy_suffix
):
    """Canonical metadata preserves current and historical parser log paths."""
    datafile = DataFileFactory.create(
        program_type=program_type,
        section=section_name,
    )
    DataFile.objects.filter(pk=datafile.pk).update(
        program_type="STALE", section="Stale Section"
    )
    datafile.refresh_from_db()

    prefix = f"{datafile.year}/{datafile.quarter}/{datafile.stt}"
    assert create_s3_log_file_path(datafile) == (
        f"{prefix}/{program_type}/{section_name}/{datafile.id}"
    )
    assert create_legacy_s3_log_file_path(datafile) == f"{prefix}/{legacy_suffix}"

    shadow = create_or_update_shadow_data_file(datafile)
    assert create_s3_log_file_path(shadow) == (
        f"{prefix}/{program_type}/{section_name}/{datafile.id}"
    )
