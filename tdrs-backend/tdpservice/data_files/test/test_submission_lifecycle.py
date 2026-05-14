"""Tests for submission lifecycle helpers."""

import pytest

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.submission_lifecycle import (
    InvalidScanResult,
    InvalidTransition,
    allowed_next_states,
    complete_datafile_av_scan,
    transition_datafile,
    validate_transition,
)
from tdpservice.data_files.test.factories import DataFileFactory


def test_valid_transitions_succeed():
    """Test allowed state transitions validate successfully."""
    first = validate_transition(
        SubmissionState.UPLOADED, SubmissionState.VIRUS_SCAN_STARTED
    )
    second = validate_transition(
        SubmissionState.VIRUS_SCAN_STARTED,
        SubmissionState.VIRUS_SCAN_COMPLETED,
    )

    assert first.previous_state == SubmissionState.UPLOADED
    assert first.next_state == SubmissionState.VIRUS_SCAN_STARTED
    assert second.previous_state == SubmissionState.VIRUS_SCAN_STARTED
    assert second.next_state == SubmissionState.VIRUS_SCAN_COMPLETED
    assert allowed_next_states(SubmissionState.UPLOADED) == {
        SubmissionState.VIRUS_SCAN_STARTED,
        SubmissionState.CANCELED,
    }


def test_invalid_transition_raises():
    """Test invalid transitions raise InvalidTransition."""
    with pytest.raises(InvalidTransition, match="uploaded to parse_completed"):
        validate_transition(SubmissionState.UPLOADED, SubmissionState.PARSE_COMPLETED)


@pytest.mark.parametrize(
    "state",
    [
        SubmissionState.COMPLETED,
        SubmissionState.CANCELED,
    ],
)
def test_terminal_states_cannot_transition(state):
    """Test terminal states reject further transitions."""
    with pytest.raises(InvalidTransition, match=f"{state.value} to uploaded"):
        validate_transition(state, SubmissionState.UPLOADED)


@pytest.mark.django_db
def test_transition_datafile_updates_state():
    """Test transition_datafile persists the expected state."""
    data_file = DataFileFactory(state=SubmissionState.UPLOADED)

    transition_datafile(
        data_file,
        SubmissionState.VIRUS_SCAN_STARTED,
        note="Picked up by AV scan worker",
    )
    data_file.refresh_from_db()

    assert data_file.state == SubmissionState.VIRUS_SCAN_STARTED


@pytest.mark.django_db
def test_transition_datafile_calls_logger_hook():
    """Test transition_datafile emits structured payloads to a logger hook."""
    data_file = DataFileFactory(state=SubmissionState.PARSE_STARTED)
    payloads = []

    transition_datafile(
        data_file,
        SubmissionState.PARSE_COMPLETED,
        note="Parser completed successfully",
        logger_hook=payloads.append,
    )

    assert payloads == [
        {
            "data_file_id": data_file.id,
            "previous_state": SubmissionState.PARSE_STARTED.value,
            "next_state": SubmissionState.PARSE_COMPLETED.value,
            "note": "Parser completed successfully",
        }
    ]


@pytest.mark.django_db
def test_transition_datafile_integration_persists_sequential_state_changes():
    """Test sequential persisted transitions on a real DataFile instance."""
    data_file = DataFileFactory(state=SubmissionState.UPLOADED)
    payloads = []

    transition_datafile(
        data_file,
        SubmissionState.VIRUS_SCAN_STARTED,
        note="Virus scan worker picked up the file",
        logger_hook=payloads.append,
    )
    data_file.refresh_from_db()

    assert data_file.state == SubmissionState.VIRUS_SCAN_STARTED

    transition_datafile(
        data_file,
        SubmissionState.VIRUS_SCAN_COMPLETED,
        note="Virus scan passed",
        logger_hook=payloads.append,
    )
    data_file.refresh_from_db()

    assert data_file.state == SubmissionState.VIRUS_SCAN_COMPLETED
    assert payloads == [
        {
            "data_file_id": data_file.id,
            "previous_state": SubmissionState.UPLOADED.value,
            "next_state": SubmissionState.VIRUS_SCAN_STARTED.value,
            "note": "Virus scan worker picked up the file",
        },
        {
            "data_file_id": data_file.id,
            "previous_state": SubmissionState.VIRUS_SCAN_STARTED.value,
            "next_state": SubmissionState.VIRUS_SCAN_COMPLETED.value,
            "note": "Virus scan passed",
        },
    ]


@pytest.mark.django_db
def test_transition_datafile_supports_parse_failed_state():
    """Test transition_datafile persists parser failures caused by exceptions."""
    data_file = DataFileFactory(state=SubmissionState.PARSE_STARTED)

    transition_datafile(
        data_file,
        SubmissionState.PARSE_FAILED,
        note="Parser raised an unexpected exception",
    )
    data_file.refresh_from_db()

    assert data_file.state == SubmissionState.PARSE_FAILED


@pytest.mark.parametrize(
    "state",
    [
        SubmissionState.PARSE_FAILED,
        SubmissionState.PARSED_WITH_ERRORS,
        SubmissionState.PARSE_COMPLETED,
    ],
)
def test_parse_outcome_states_can_reparse(state):
    """Test parsed files can transition back to parsing for reparse."""
    transition = validate_transition(state, SubmissionState.PARSE_STARTED)

    assert transition.previous_state == state
    assert transition.next_state == SubmissionState.PARSE_STARTED


@pytest.mark.django_db
def test_complete_datafile_av_scan_clean_transitions_to_virus_scan_completed():
    """Clean AV completion should move a DataFile into virus scan completed."""
    data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_STARTED)
    payloads = []

    result_file, transition_occurred = complete_datafile_av_scan(
        data_file,
        scan_result="clean",
        note="AV callback reported clean file",
        logger_hook=payloads.append,
    )
    data_file.refresh_from_db()

    assert transition_occurred is True
    assert result_file.id == data_file.id
    assert data_file.state == SubmissionState.VIRUS_SCAN_COMPLETED
    assert payloads == [
        {
            "data_file_id": data_file.id,
            "previous_state": SubmissionState.VIRUS_SCAN_STARTED.value,
            "next_state": SubmissionState.VIRUS_SCAN_COMPLETED.value,
            "scan_result": "CLEAN",
            "note": "AV callback reported clean file",
        }
    ]


@pytest.mark.django_db
def test_complete_datafile_av_scan_fail_transitions_to_virus_scan_failed():
    """Infected/failed AV completion should move a DataFile into scan failed."""
    data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_STARTED)
    payloads = []

    result_file, transition_occurred = complete_datafile_av_scan(
        data_file,
        scan_result="infected",
        note="AV callback reported infection",
        logger_hook=payloads.append,
    )
    data_file.refresh_from_db()

    assert transition_occurred is True
    assert result_file.id == data_file.id
    assert data_file.state == SubmissionState.VIRUS_SCAN_FAILED
    assert payloads == [
        {
            "data_file_id": data_file.id,
            "previous_state": SubmissionState.VIRUS_SCAN_STARTED.value,
            "next_state": SubmissionState.VIRUS_SCAN_FAILED.value,
            "scan_result": "INFECTED",
            "note": "AV callback reported infection",
        }
    ]


@pytest.mark.django_db
def test_complete_datafile_av_scan_normalizes_scan_result_values():
    """Scan result handling should be case-insensitive and trim whitespace."""
    data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_STARTED)

    result_file, transition_occurred = complete_datafile_av_scan(
        data_file, scan_result="  CLEAN  "
    )
    data_file.refresh_from_db()

    assert transition_occurred is True
    assert result_file.id == data_file.id
    assert data_file.state == SubmissionState.VIRUS_SCAN_COMPLETED


@pytest.mark.django_db
def test_complete_datafile_av_scan_out_of_order_noops_with_log_payload():
    """Out-of-order completion should no-op and emit structured context."""
    data_file = DataFileFactory(state=SubmissionState.PARSE_STARTED)
    payloads = []

    result_file, transition_occurred = complete_datafile_av_scan(
        data_file,
        scan_result="clean",
        logger_hook=payloads.append,
    )
    data_file.refresh_from_db()

    assert transition_occurred is False
    assert result_file.id == data_file.id
    assert data_file.state == SubmissionState.PARSE_STARTED
    assert payloads == [
        {
            "data_file_id": data_file.id,
            "previous_state": SubmissionState.PARSE_STARTED.value,
            "next_state": SubmissionState.VIRUS_SCAN_COMPLETED.value,
            "scan_result": "CLEAN",
            "note": "Ignoring out-of-order AV completion result for DataFile.",
        }
    ]


@pytest.mark.django_db
def test_complete_datafile_av_scan_duplicate_result_noops_with_log_payload():
    """Repeated callbacks with the same terminal result should be idempotent."""
    data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_COMPLETED)
    payloads = []

    result_file, transition_occurred = complete_datafile_av_scan(
        data_file,
        scan_result="clean",
        logger_hook=payloads.append,
    )
    data_file.refresh_from_db()

    assert transition_occurred is False
    assert result_file.id == data_file.id
    assert data_file.state == SubmissionState.VIRUS_SCAN_COMPLETED
    assert payloads == [
        {
            "data_file_id": data_file.id,
            "previous_state": SubmissionState.VIRUS_SCAN_COMPLETED.value,
            "next_state": SubmissionState.VIRUS_SCAN_COMPLETED.value,
            "scan_result": "CLEAN",
            "note": "Duplicate AV completion result; no-op.",
        }
    ]


@pytest.mark.django_db
def test_complete_datafile_av_scan_strict_out_of_order_raises():
    """Strict mode should raise for out-of-order callbacks."""
    data_file = DataFileFactory(state=SubmissionState.PARSE_STARTED)

    with pytest.raises(
        InvalidTransition,
        match="Cannot apply AV scan completion while DataFile is in parse_started",
    ):
        complete_datafile_av_scan(data_file, scan_result="clean", strict=True)


def test_complete_datafile_av_scan_rejects_unknown_scan_result():
    """Unknown scan result values should fail fast."""
    data_file = DataFileFactory.build(state=SubmissionState.VIRUS_SCAN_STARTED)

    with pytest.raises(InvalidScanResult, match="Unsupported AV scan result"):
        complete_datafile_av_scan(data_file, scan_result="MAYBE")
