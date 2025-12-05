# Submission State Machine for File Processing

## Purpose
Define and enforce a clear lifecycle for uploaded files so parsing, ingest, and triage share a consistent contract. This is a precursor to the parser refactor to avoid churn and make status handling predictable.

## States
`uploaded` → `virus_scanning` → (`scan_failed` | `validated`) → `parsing` → (`parsed_with_errors` | `parsed_clean`) → `ingesting` → (`ingest_failed` | `completed`). Any active state can transition to `canceled`.

## Allowed transitions (code sketch)
```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable

class SubmissionState(str, Enum):
    UPLOADED = "uploaded"
    VIRUS_SCANNING = "virus_scanning"
    SCAN_FAILED = "scan_failed"
    VALIDATED = "validated"
    PARSING = "parsing"
    PARSED_WITH_ERRORS = "parsed_with_errors"
    PARSED_CLEAN = "parsed_clean"
    INGESTING = "ingesting"
    INGEST_FAILED = "ingest_failed"
    COMPLETED = "completed"
    CANCELED = "canceled"

ALLOWED_TRANSITIONS: Dict[SubmissionState, Iterable[SubmissionState]] = {
    SubmissionState.UPLOADED: {SubmissionState.VIRUS_SCANNING, SubmissionState.CANCELED},
    SubmissionState.VIRUS_SCANNING: {
        SubmissionState.SCAN_FAILED,
        SubmissionState.VALIDATED,
        SubmissionState.CANCELED,
    },
    SubmissionState.SCAN_FAILED: {SubmissionState.CANCELED},
    SubmissionState.VALIDATED: {SubmissionState.PARSING, SubmissionState.CANCELED},
    SubmissionState.PARSING: {
        SubmissionState.PARSED_WITH_ERRORS,
        SubmissionState.PARSED_CLEAN,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSED_WITH_ERRORS: {SubmissionState.INGESTING, SubmissionState.CANCELED},
    SubmissionState.PARSED_CLEAN: {SubmissionState.INGESTING, SubmissionState.CANCELED},
    SubmissionState.INGESTING: {
        SubmissionState.INGEST_FAILED,
        SubmissionState.COMPLETED,
        SubmissionState.CANCELED,
    },
    SubmissionState.INGEST_FAILED: {SubmissionState.CANCELED},
    SubmissionState.COMPLETED: set(),
    SubmissionState.CANCELED: set(),
}

class InvalidTransition(Exception):
    ...

@dataclass
class SubmissionLifecycle:
    state: SubmissionState
    history: list[str] = field(default_factory=list)

    def transition(self, next_state: SubmissionState, note: str = "") -> None:
        if next_state not in ALLOWED_TRANSITIONS[self.state]:
            raise InvalidTransition(f"{self.state} → {next_state} not allowed")
        self.history.append(f"{self.state} -> {next_state}: {note}")
        self.state = next_state
```

## Transition helpers (examples)
```python
def on_upload(lifecycle: SubmissionLifecycle):
    lifecycle.transition(SubmissionState.VIRUS_SCANNING, "file accepted; queued for AV")

def on_scan_complete(lifecycle: SubmissionLifecycle, clean: bool):
    lifecycle.transition(
        SubmissionState.VALIDATED if clean else SubmissionState.SCAN_FAILED,
        "scan pass" if clean else "scan flagged",
    )

def on_header_validated(lifecycle: SubmissionLifecycle):
    lifecycle.transition(SubmissionState.PARSING, "header/pre-parse checks passed")

def on_parsing_finished(lifecycle: SubmissionLifecycle, has_errors: bool):
    lifecycle.transition(
        SubmissionState.PARSED_WITH_ERRORS if has_errors else SubmissionState.PARSED_CLEAN,
        "parse finished with errors" if has_errors else "parse finished clean",
    )

def on_ingest_start(lifecycle: SubmissionLifecycle):
    lifecycle.transition(SubmissionState.INGESTING, "begin persisting records/errors")

def on_ingest_finish(lifecycle: SubmissionLifecycle, ok: bool):
    lifecycle.transition(
        SubmissionState.COMPLETED if ok else SubmissionState.INGEST_FAILED,
        "ingest success" if ok else "ingest failure",
    )

def on_cancel(lifecycle: SubmissionLifecycle, reason: str = ""):
    if lifecycle.state not in {SubmissionState.COMPLETED, SubmissionState.CANCELED}:
        lifecycle.state = SubmissionState.CANCELED
        lifecycle.history.append(f"canceled from {lifecycle.state}: {reason}")
```

## Integrating with Django models
```python
from django.db import transaction
from tdpservice.data_files.models import DataFile

def transition_datafile(data_file: DataFile, next_state: SubmissionState, note: str = ""):
    with transaction.atomic():
        lifecycle = SubmissionLifecycle(SubmissionState(data_file.state))
        lifecycle.transition(next_state, note)
        data_file.state = lifecycle.state.value
        data_file.save(update_fields=["state"])
        # Optionally persist history to an audit table
```

## Guardrails and rollout
- Enforce transitions server-side; do not trust client input.
- Use atomic transactions when updating state plus side effects (enqueue parse, write summaries).
- Log every transition with correlation IDs (data_file_id, reparse_id) and optional audit trail.
- Feature flag initial enforcement to allow rollback.
- Provide a migration to set a default state for existing `DataFile` rows.

## Implementation Tickets (small, incremental)
1. **Add state enum + migration**  
   - Add `SubmissionState` enum and `state` field to `DataFile` (default `uploaded`) via migration.  
   - Acceptance: migration applies; existing rows have a default; no code paths changed yet.

2. **Transition helper module**  
   - Implement `SubmissionLifecycle` and `transition_datafile` helper with validation and logging hooks.  
   - Acceptance: unit tests cover allowed/blocked transitions; no callers migrated yet.

3. **Wire upload → virus_scanning transition**  
   - Update upload path to set state to `virus_scanning` via helper; add log/audit.  
   - Acceptance: upload tests updated; illegal transitions blocked.

4. **Wire scan callback → validated/scan_failed**  
   - Update AV scan completion to transition to `validated` or `scan_failed` via helper.  
   - Acceptance: tests for both branches; logs include data_file_id.

5. **Wire parser entry/exit**  
   - On parser start, transition to `parsing`; on completion, to `parsed_clean`/`parsed_with_errors`.  
   - Acceptance: parser tests assert resulting state; failures do not leave state stale.

6. **Wire ingest start/finish**  
   - Transition to `ingesting` before persistence and to `completed`/`ingest_failed` afterward.  
   - Acceptance: ingest path updates state correctly; failure path covered.

7. **Add cancel path**  
   - Expose a cancel hook that transitions to `canceled` from active states; ensure downstream work is halted.  
   - Acceptance: cancel test added; illegal cancels blocked.

8. **Feature flag + audit logging**  
   - Add a flag to enforce/relax transition validation; add optional audit table or structured log per transition.  
   - Acceptance: flag toggles enforcement; audit/log entries emitted with correlation IDs.
