"""Helpers for DataFile submission state transitions."""

import logging
from dataclasses import dataclass
from typing import Callable, Dict, Iterable

from tdpservice.data_files.enums import SubmissionState

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TransitionRecord:
    """In-memory record of a single submission state transition."""

    previous_state: SubmissionState
    next_state: SubmissionState
    note: str = ""


class InvalidTransition(ValueError):
    """Raised when an invalid submission state transition is attempted."""


class InvalidScanResult(ValueError):
<<<<<<< HEAD
    """Raised when an unrecognized scan result value is provided."""
=======
    """Raised when an AV scan result cannot be mapped to a submission state."""
>>>>>>> 374a0a78b84497f675ca930ce9fc1d6900b8b18b


ALLOWED_TRANSITIONS: Dict[SubmissionState, Iterable[SubmissionState]] = {
    SubmissionState.UPLOADED: {
        SubmissionState.VIRUS_SCAN_STARTED,
        SubmissionState.CANCELED,
    },
    SubmissionState.VIRUS_SCAN_STARTED: {
        SubmissionState.VIRUS_SCAN_FAILED,
        SubmissionState.VIRUS_SCAN_COMPLETED,
        SubmissionState.CANCELED,
    },
    SubmissionState.VIRUS_SCAN_FAILED: {
        SubmissionState.CANCELED,
    },
    SubmissionState.VIRUS_SCAN_COMPLETED: {
        SubmissionState.PARSE_STARTED,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSE_STARTED: {
        SubmissionState.PARSE_FAILED,
        SubmissionState.PARSED_WITH_ERRORS,
        SubmissionState.PARSE_COMPLETED,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSE_FAILED: {
        SubmissionState.PARSE_STARTED,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSED_WITH_ERRORS: {
        SubmissionState.PARSE_STARTED,
        SubmissionState.COMPLETED,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSE_COMPLETED: {
        SubmissionState.PARSE_STARTED,
        SubmissionState.COMPLETED,
        SubmissionState.CANCELED,
    },
    SubmissionState.STUCK: {
        SubmissionState.CANCELED,
    },
    SubmissionState.COMPLETED: set(),
    SubmissionState.CANCELED: set(),
}


def coerce_submission_state(state) -> SubmissionState:
    """Normalize a state value into a SubmissionState enum."""
    if isinstance(state, SubmissionState):
        return state
    return SubmissionState(state)


def allowed_next_states(current_state) -> set[SubmissionState]:
    """Return the allowed next states for the given current state."""
    normalized_current_state = coerce_submission_state(current_state)
    return set(ALLOWED_TRANSITIONS[normalized_current_state])


def validate_transition(current_state, next_state) -> TransitionRecord:
    """Validate a transition request and return a transition record."""
    normalized_current_state = coerce_submission_state(current_state)
    normalized_next_state = coerce_submission_state(next_state)

    if normalized_next_state not in allowed_next_states(normalized_current_state):
        raise InvalidTransition(
            f"Cannot transition submission from {normalized_current_state.value} "
            + f"to {normalized_next_state.value}."
        )

    return TransitionRecord(
        previous_state=normalized_current_state,
        next_state=normalized_next_state,
    )


def transition_datafile(
    data_file,
    next_state,
    note="",
    logger_hook: Callable | None = None,
    log_fields: dict | None = None,
):
    """Safely transition a DataFile.state value and persist the new state."""
    transition = validate_transition(data_file.state, next_state)
    transition = TransitionRecord(
        previous_state=transition.previous_state,
        next_state=transition.next_state,
        note=note,
    )

    data_file.state = transition.next_state
    data_file.save(update_fields=["state"])

    log_payload = {
        "data_file_id": data_file.id,
        "previous_state": transition.previous_state.value,
        "next_state": transition.next_state.value,
        "note": note,
    }
    if log_fields:
        log_payload.update(log_fields)

    if logger_hook is not None:
        logger_hook(log_payload)
    else:
        logger.info("DataFile submission state transition", extra=log_payload)

    return data_file


def _normalize_scan_result(scan_result) -> str:
    """Normalize a scan result value into an upper-case token."""
    value = getattr(scan_result, "value", scan_result)
    return str(value).strip().upper()


def _next_state_for_scan_result(scan_result) -> SubmissionState:
    """Map an AV scan result token to a submission lifecycle state."""
    normalized = _normalize_scan_result(scan_result)

    if normalized in {"CLEAN", "PASS", "PASSED", "OK"}:
        return SubmissionState.VIRUS_SCAN_COMPLETED

    if normalized in {"INFECTED", "FAIL", "FAILED", "FLAGGED", "ERROR"}:
        return SubmissionState.VIRUS_SCAN_FAILED

    raise InvalidScanResult(f"Unsupported AV scan result: {scan_result}")


def complete_datafile_av_scan(
    data_file,
    scan_result,
    note="",
    logger_hook: Callable | None = None,
    strict=False,
):
    """Apply AV scan completion result to DataFile state.

    Expected transition:
<<<<<<< HEAD
    - VIRUS_SCAN_STARTED -> VIRUS_SCAN_COMPLETED (clean)
    - VIRUS_SCAN_STARTED -> VIRUS_SCAN_FAILED (infected/error/flagged)

    By default this function is idempotent and will no-op for out-of-order
    results. Set strict=True to raise InvalidTransition on unexpected states.

    Args:
        data_file: DataFile instance to update
        scan_result: Scan result value (CLEAN, INFECTED, ERROR, etc.)
        note: Optional note for logging
        logger_hook: Optional callable for custom logging
        strict: If True, raise InvalidTransition on unexpected states

    Returns:
        Updated DataFile instance
=======
    - virus_scan_started -> virus_scan_completed (clean)
    - virus_scan_started -> virus_scan_failed (infected/error/flagged)

    By default this function is idempotent and will no-op for out-of-order
    results. Set strict=True to raise InvalidTransition on unexpected states.
>>>>>>> 374a0a78b84497f675ca930ce9fc1d6900b8b18b
    """
    target_state = _next_state_for_scan_result(scan_result)
    previous_state = coerce_submission_state(data_file.state)
    normalized_scan_result = _normalize_scan_result(scan_result)

<<<<<<< HEAD
    # Idempotent: if already in target state, no-op
=======
>>>>>>> 374a0a78b84497f675ca930ce9fc1d6900b8b18b
    if previous_state == target_state:
        payload = {
            "data_file_id": data_file.id,
            "previous_state": previous_state.value,
            "next_state": target_state.value,
            "scan_result": normalized_scan_result,
<<<<<<< HEAD
            "note": "Duplicate scan result, already in target state (no-op)",
=======
            "note": note or "Duplicate AV completion result; no-op.",
>>>>>>> 374a0a78b84497f675ca930ce9fc1d6900b8b18b
        }
        if logger_hook is not None:
            logger_hook(payload)
        else:
<<<<<<< HEAD
            logger.info(
                "AV scan completion no-op: already in target state", extra=payload
            )
        return data_file

    # Handle out-of-order results
    if previous_state not in {SubmissionState.VIRUS_SCAN_STARTED}:
=======
            logger.info("DataFile AV scan completion no-op", extra=payload)
        return data_file

    if previous_state != SubmissionState.VIRUS_SCAN_STARTED:
        if strict:
            raise InvalidTransition(
                f"Cannot apply AV scan completion while DataFile is in "
                f"{previous_state.value}."
            )

>>>>>>> 374a0a78b84497f675ca930ce9fc1d6900b8b18b
        payload = {
            "data_file_id": data_file.id,
            "previous_state": previous_state.value,
            "next_state": target_state.value,
            "scan_result": normalized_scan_result,
<<<<<<< HEAD
            "note": f"Out-of-order scan result from state {previous_state.value}",
        }

        if strict:
            logger.error("AV scan completion out-of-order (strict mode)", extra=payload)
            raise InvalidTransition(
                f"Cannot apply scan result {scan_result} from state {previous_state.value}"
            )
        else:
            if logger_hook is not None:
                logger_hook(payload)
            else:
                logger.warning("AV scan completion out-of-order (ignoring)", extra=payload)
            return data_file, False

    # Normal transition - add scan_result to logging payload
    completion_note = note or f"AV scan completed with result: {normalized_scan_result}"
    
    # Custom logger hook that includes scan_result
    def scan_logger_hook(log_payload):
        enriched_payload = {**log_payload, "scan_result": normalized_scan_result}
        if logger_hook is not None:
            logger_hook(enriched_payload)
        else:
            logger.info("AV scan completion transition", extra=enriched_payload)
    
    transitioned_file = transition_datafile(
        data_file,
        target_state,
        note=completion_note,
        logger_hook=scan_logger_hook,
    )
    return transitioned_file, True
=======
            "note": note
            or "Ignoring out-of-order AV completion result for DataFile.",
        }
        if logger_hook is not None:
            logger_hook(payload)
        else:
            logger.warning("DataFile AV scan completion out-of-order", extra=payload)
        return data_file

    return transition_datafile(
        data_file,
        target_state,
        note=note or "Applied AV scan completion result.",
        logger_hook=logger_hook,
        log_fields={"scan_result": normalized_scan_result},
    )
>>>>>>> 374a0a78b84497f675ca930ce9fc1d6900b8b18b
