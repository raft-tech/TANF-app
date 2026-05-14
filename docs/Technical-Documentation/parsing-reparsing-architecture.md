# Parsing and Reparsing Architecture

- **Status:** Internal reference documentation
- **Scope:** TDP data file upload, parsing, validation, error reporting, and reparsing
- **Last updated:** 2026-05-14

---

## Purpose

This document explains how TDP moves a submitted data file from upload through parser outcome, and how admin-triggered reparsing reuses that same path. It is intended to explain the system structure, behavior rules, and operational tradeoffs. It is not a line-by-line guide to the implementation.

Use this document when you need to understand:

- which part of the system owns each stage of a submission,
- how parser outcomes are represented,
- how validation errors affect records, summaries, reports, and emails,
- what reparsing resets before it runs, and
- which behavior is important to preserve during refactors.

For implementation details, use the source files referenced in [Where to Look](#where-to-look).

---

## Core Concepts

### `DataFile`

`DataFile` represents the uploaded submission. It owns metadata such as program, section, reporting period, uploader, STT, and the uploaded file itself. It also has a lifecycle `state` that describes where the submission is in the upload and parsing process.

Examples of lifecycle state:

- uploaded,
- virus scan started or completed,
- parse started,
- parse completed,
- parse completed with errors,
- parse failed.

### `DataFileSummary`

`DataFileSummary` represents the parser outcome for one `DataFile`. It is the primary source used by parser emails, error report views, aggregate counts, and user-facing parse status.

The important distinction is:

- `DataFile.state` describes the lifecycle of processing the file.
- `DataFileSummary.status` describes the parser outcome.

Those two concepts usually move together, but they answer different questions. Refactors should keep that distinction explicit.

### Parsed Records

Parsed records are stored in program- and section-specific search index models, such as TANF, SSP, Tribal TANF, FRA, and audit record tables. They are tied back to the `DataFile`.

The parser may create records before it knows whether every cross-record validation has passed. Some later validation results can remove records that were already written.

### `ParserError`

`ParserError` stores validation and parser errors for a submitted file. Active errors are the source for parser outcome, aggregate summaries, and generated Excel reports.

Errors are categorized by severity and behavior. Some errors allow records to remain accepted with errors; others reject records or cases.

### Error Report

The Excel error report is generated after parsing from active `ParserError` rows and stored on the `DataFileSummary`. It is a derived artifact, not the source of truth.

### Reparse Metadata

Reparse metadata tracks admin-triggered reparse batches and per-file progress. It lets admins see which files were selected, which files finished, whether a file succeeded, and how record counts changed.

---

## System Shape

The parsing path has five broad stages:

1. **Upload and scan**
   The API validates the request, creates a `DataFile` metadata row without storing the uploaded file, runs antivirus scanning, and queues parsing only if the file is safe.

2. **Background parse orchestration**
   A Celery worker loads the file, creates a summary, selects the parser family, runs parsing and validation, and updates lifecycle state.

3. **Parsing and validation**
   The selected parser converts rows into structured records and validation errors. Some validation is local to a row or field; some validation compares records in the same case or file.

4. **Persistence and summarization**
   The parser writes records and errors to the database, computes the parser outcome, updates aggregate counts, and applies cleanup rules for rejected cases or duplicate records.

5. **Reports and notifications**
   TDP generates an Excel error report and sends the appropriate notification email when the parse outcome calls for one.

The same background parse path is used for first-time submissions and reparses. Reparsing changes the setup and tracking around the parse, not the core parser behavior.

---

## First-Time Submission Flow

When a user uploads a file:

1. The API validates the submission metadata and file extension.
2. `DataFileSerializer.create()` creates a `DataFile` row in the initial upload state, with no uploaded file stored yet.
3. TDP advances the row to virus-scan-started and scans the uploaded file with ClamAV during the request.
4. If the file is unsafe or the scanner is unavailable, the request fails, the `DataFile` remains for lifecycle visibility, the uploaded file is not stored, and no parser task is queued.
5. If the file is safe, TDP marks the scan complete, stores the uploaded file, and queues a parse task.
6. The API returns after the task is queued; parsing continues asynchronously.

When the parse task runs:

1. It creates a `DataFileSummary` in a pending parser-outcome state.
2. It selects the parser family based on program, section, and audit status.
3. It parses rows, writes valid records, and records validation errors.
4. It applies cross-record rules such as case consistency and duplicate handling.
5. It computes the final `DataFileSummary.status`.
6. It maps the parser outcome back onto `DataFile.state`.
7. It generates an error report and stores it on the summary.
8. It sends a notification when the outcome should be surfaced to users.

---

## Parser Families

TDP currently has three parser families:

| Parser family | Handles | Notes |
|---|---|---|
| TANF data report parser | TANF, SSP-MOE, and Tribal TANF active, closed, aggregate, and stratum files | Uses record schemas and case-level validation rules. |
| FRA parser | FRA Work Outcome / TANF Exiters files | Handles CSV and XLSX inputs and uses FRA-specific validation/reporting behavior. |
| Program audit parser | Program Integrity Audit submissions | Shares much of the TANF flow but preserves duplicate records while still reporting duplicate errors. |

The parser family determines how rows are decoded, which schemas are used, which validation rules apply, and which destination models receive parsed records.

---

## Validation Model

Validation is layered. The layers matter because each one has a different effect on parser outcome and persisted records.

| Layer | What it checks | Typical outcome |
|---|---|---|
| File pre-check | File-level viability, such as malformed header or unreadable content | Can reject the entire file. |
| Record pre-check | Whether an individual row can be interpreted as a known record shape | Can reject the row or cause partial acceptance. |
| Field validation | Field-level format, range, and required-value rules | Usually accepts the file with errors. |
| Value consistency | Cross-field rules inside a record | Usually accepts the file with errors. |
| Case consistency | Cross-record rules for a case or grouped records | Can reject related records after they were parsed. |

This layered model lets TDP keep useful records when errors are limited, while still rejecting data that cannot be trusted structurally.

### Example: Field Error

A TANF record may parse successfully while one field contains a value outside the allowed range. In that case:

- the parsed record can remain stored,
- a `ParserError` is written,
- the summary may become `Accepted with Errors`, and
- the error report includes the field-level error.

### Example: Case Consistency Error

A TANF case may contain individually valid records that do not make sense together. In that case:

- the parser writes case-consistency errors,
- affected case records may be removed from the accepted record tables,
- the file may become partially accepted, and
- the error report explains which records were rejected.

### Example: Program Audit Duplicates

Program audit submissions report duplicate records differently from standard TANF parsing. Duplicate records are reported as errors, but the records are retained. This preserves audit review data while still flagging the problem.

### Example: FRA Error

FRA files follow a different shape from TANF fixed-width submissions. FRA validation still writes `ParserError` rows and produces an Excel error report, but the parser family and report format are FRA-specific.

---

## Parser Outcome Rules

`DataFileSummary.status` is derived from parser errors and record outcomes. The exact database values live in the model, but the behavior is:

- **Accepted** means no active parser errors remain.
- **Accepted with errors** means records were created and errors exist that do not require rejecting those records.
- **Partially accepted** means some records or cases were rejected while others were accepted.
- **Rejected** means the file did not produce acceptable records or hit a file-level failure.
- **Pending** means parsing has not finished or the summary has not been updated yet.

`DataFile.state` is then updated from that parser outcome so the submission lifecycle reflects parse completion, completion with errors, or failure.

---

## Error Reports and Notifications

Error reports and emails are downstream of parser outcome.

The error report:

- is generated from active `ParserError` rows,
- is stored on `DataFileSummary`,
- is attempted for both successful and failed parses, and
- can be missing if parsing fails before the summary exists or if report generation itself fails.

Notification emails:

- are sent to approved Data Analysts for the submitting STT,
- use FRA access rules for FRA files,
- use parser outcome to choose the email content, and
- are not the source of parser status.

Because reports are generated after parsing, there is a short timing window where the parse outcome may be known before the error report file is stored.

---

## Reparsing

Reparsing is an admin operation for rerunning parser logic against existing submissions. It exists because parser logic, schemas, and error handling can change after a file was originally submitted.

Before a reparse starts, TDP creates a batch-level reparse record and cleans old parser output for selected files:

- previous parser errors,
- parsed search index records,
- the old `DataFileSummary`,
- and related derived parser artifacts.

Each selected file is then queued through the same parse task used by a first-time submission. Per-file reparse metadata tracks start time, finish time, success, and record-count changes.

### Why Reparsing Cleans First

The parser is not designed as an idempotent upsert pipeline. It expects to create a new summary and write a fresh set of records and errors. Cleaning first avoids mixing old parser results with new ones.

The tradeoff is that a failed or interrupted reparse can leave a file without the previous successful parser outputs until the issue is repaired and rerun.

### Reparse Notifications

Reparse notifications are intentionally quieter than first-time submission notifications. If a file was previously accepted and remains accepted after reparse, notification can be suppressed. Other outcome changes can trigger reprocessed email templates.

---

## Retry and Failure Behavior

The parse task does not automatically retry when it crashes. Operationally, that means:

- a failed or stalled parse needs human inspection,
- admins usually recover by reparsing,
- partial database writes are possible if failure happens mid-parse, and
- cleanup behavior is important but not a substitute for a whole-file transaction.

TDP has scheduled monitoring for stuck files. It identifies submissions that have not reached a completed parser outcome within the expected window and notifies OFA System Admins. It does not repair the file automatically.

---

## Refactor Considerations

These are the behavior contracts that are easy to break accidentally:

1. **Keep lifecycle state and parser outcome distinct.**
   `DataFile.state` and `DataFileSummary.status` should not be collapsed unless the replacement clearly supports both lifecycle tracking and parser outcome reporting.

2. **Clarify ownership before changing shared parser state.**
   `DataFile`, `DataFileSummary`, `ParserError`, error reports, notification logic, and reparse metadata are updated by different parts of the pipeline. Refactors should make the owner of each write explicit so status, counts, and user-facing artifacts do not drift apart.

3. **Do not treat the parser as idempotent without changing cleanup.**
   First-time parsing assumes no existing summary for the file. Reparsing works by deleting old parser output before queuing a fresh parse.

4. **Preserve severity semantics.**
   Field, value, record, case, and file-level errors affect records and user-facing status differently.

5. **Be careful with mid-parse persistence.**
   Records and errors are written in batches. Any change to rollback behavior should account for partial writes.

6. **Keep error reports derived from `ParserError`.**
   The report should reflect stored active errors, not a separate source of truth.

7. **Preserve program-specific differences.**
   TANF, SSP, Tribal TANF, FRA, and program audit submissions share concepts but do not all share duplicate handling, file shape, or report behavior.

8. **Handle reparse progress independently from parse success.**
   Reparse metadata is the only batch-level view of progress across multiple files.

9. **Treat reparsing and duplicate task delivery as race-condition risks.**
   Reparse cleanup, parse task enqueueing, and parser writes happen in separate steps. Overlapping reparses or duplicate task execution can race unless the workflow explicitly coordinates file selection, cleanup, and final status writes.

---

## Where to Look

The following files are useful anchors when you need implementation details:

| Area | Primary files |
|---|---|
| Upload and lifecycle transitions | `tdrs-backend/tdpservice/data_files/views.py`, `tdrs-backend/tdpservice/data_files/submission_lifecycle.py` |
| Submission validation | `tdrs-backend/tdpservice/data_files/serializers.py` |
| Parse task orchestration | `tdrs-backend/tdpservice/scheduling/parser_task.py` |
| Parser selection | `tdrs-backend/tdpservice/parsers/factory.py` |
| Shared parser behavior | `tdrs-backend/tdpservice/parsers/parser_classes/base_parser.py` |
| TANF, SSP, Tribal parser behavior | `tdrs-backend/tdpservice/parsers/parser_classes/tdr_parser.py` |
| FRA parser behavior | `tdrs-backend/tdpservice/parsers/parser_classes/fra_parser.py` |
| Program audit behavior | `tdrs-backend/tdpservice/parsers/parser_classes/program_audit_parser.py` |
| Schema and row validation | `tdrs-backend/tdpservice/parsers/schema_manager.py`, `tdrs-backend/tdpservice/parsers/schemas/` |
| Error report generation | `tdrs-backend/tdpservice/data_files/error_reports.py` |
| Reparse setup and cleanup | `tdrs-backend/tdpservice/search_indexes/reparse.py`, `tdrs-backend/tdpservice/data_files/tasks.py` |
| Parser outcome models | `tdrs-backend/tdpservice/parsers/models.py` |

---

## Documentation Maintenance Guidance

Keep this document stable by documenting behavior rather than control flow. Avoid adding:

- method-level call chains,
- argument names,
- exception-handling mechanics,
- diagrams that duplicate code structure,
- or implementation details that must be updated with every refactor.

When behavior changes, update the relevant rule or example here and link to the implementation for details.
