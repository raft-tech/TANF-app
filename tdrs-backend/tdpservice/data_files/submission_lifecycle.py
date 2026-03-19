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


ALLOWED_TRANSITIONS: Dict[SubmissionState, Iterable[SubmissionState]] = {
    SubmissionState.UPLOADED: {
        SubmissionState.VIRUS_SCAN_STARTED,
        SubmissionState.CANCELED,
    },
    SubmissionState.VIRUS_SCAN_STARTED: {
        SubmissionState.VIRUS_SCAN_FAILED,
        SubmissionState.VIRUS_SCAN_SUCCESSFUL,
        SubmissionState.CANCELED,
    },
    SubmissionState.VIRUS_SCAN_FAILED: {
        SubmissionState.CANCELED,
    },
    SubmissionState.VIRUS_SCAN_SUCCESSFUL: {
        SubmissionState.PARSE_STARTED,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSE_STARTED: {
        SubmissionState.PARSED_WITH_ERRORS,
        SubmissionState.PARSE_COMPLETED,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSED_WITH_ERRORS: {
        SubmissionState.COMPLETED,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSE_COMPLETED: {
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


class SubmissionLifecycle:
    """Validate and record in-memory submission state transitions."""

    def __init__(self, initial_state):
        self.current_state = coerce_submission_state(initial_state)
        self.history: list[TransitionRecord] = []
        self.messages: list[str] = []

    def allowed_next_states(self) -> set[SubmissionState]:
        """Return the allowed next states for the current state."""
        return set(ALLOWED_TRANSITIONS[self.current_state])

    def validate_transition(self, next_state) -> SubmissionState:
        """Validate the requested transition and return the normalized next state."""
        normalized_next_state = coerce_submission_state(next_state)

        if normalized_next_state not in self.allowed_next_states():
            raise InvalidTransition(
                f"Cannot transition submission from {self.current_state.value} "
                + f"to {normalized_next_state.value}."
            )

        return normalized_next_state

    def transition(self, next_state, note="") -> TransitionRecord:
        """Apply a validated transition and record it in-memory."""
        normalized_next_state = self.validate_transition(next_state)
        record = TransitionRecord(
            previous_state=self.current_state,
            next_state=normalized_next_state,
            note=note,
        )
        self.current_state = normalized_next_state
        self.history.append(record)

        if note:
            self.messages.append(note)

        return record


def transition_datafile(
    data_file,
    next_state,
    note="",
    logger_hook: Callable | None = None,
):
    """Safely transition a DataFile.state value and persist the new state."""
    lifecycle = SubmissionLifecycle(data_file.state)
    transition = lifecycle.transition(next_state, note=note)

    data_file.state = transition.next_state
    data_file.save(update_fields=["state"])

    log_payload = {
        "data_file_id": data_file.id,
        "previous_state": transition.previous_state.value,
        "next_state": transition.next_state.value,
        "note": note,
    }

    if logger_hook is not None:
        logger_hook(log_payload)
    else:
        logger.info("DataFile submission state transition", extra=log_payload)

    return data_file
