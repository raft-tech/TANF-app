# Submit and retrieve data files with the TDP API

Use the TANF Data Portal (TDP) API to submit reporting files from your own system,
check processing results, download submitted files, and retrieve Excel error
reports. A DataFile represents one submitted version of a file.

Start with [OIDC authentication and access tokens](authentication.md). You need
an active, approved TDP account with a role that permits each requested operation.
Data Analysts can access their assigned State, Territory, or Tribe (STT).
Regional Staff can list submissions and download error reports within their
assigned regions, but cannot submit files or download original files. A token
does not expand your account's permissions.

## API reference and example setup

Use the Swagger UI at **`<API_BASE_URL>/swagger/`** for your environment's generated
request and response schemas. For example, the production routes are
[Swagger](https://tanfdata.acf.hhs.gov/swagger/),
[ReDoc](https://tanfdata.acf.hhs.gov/redocs/), and
[OpenAPI JSON](https://tanfdata.acf.hhs.gov/swagger.json).
Use your assigned environment's hostname for testing; availability and enabled
programs may differ by environment. In Swagger, find the `data_files` operations
with the paths below. The examples here use the public `/v1/` API.

| Operation | Method | Path | Successful response |
| --- | --- | --- | --- |
| Create a submission | `POST` | `/v1/data_files/` | `201`, JSON object |
| List submissions | `GET` | `/v1/data_files/` | `200`, JSON array |
| Download a submitted file | `GET` | `/v1/data_files/{id}/download/` | `200`, file bytes |
| Download an error report | `GET` | `/v1/data_files/{id}/download_error_report/` | `200`, Excel `.xlsx` bytes |

Keep trailing slashes, including on POST requests. `{id}` means the numeric
DataFile ID returned by create or list, not an STT ID, filename, or version number.

The examples use curl in a Bash-compatible terminal. The
[authentication guide](authentication.md#before-you-start) explains prerequisites
and obtaining `ACCESS_TOKEN`. Replace all example values with your own:

```bash
export API_BASE_URL='https://your-tdp-host.example.org'
export STT_ID='123'
export REPORT_YEAR='2026'
export REPORT_QUARTER='Q1'
# ACCESS_TOKEN must already contain your OIDC access token.
```

All data below is illustrative. Test using an environment and data approved by
your organization. Submission files must follow the applicable reporting format;
renaming a file does not convert its contents.

## Create a submission

`POST /v1/data_files/`

Send **`multipart/form-data`**, including the actual file bytes. JSON bodies are
not supported for this operation. With curl, `--form` creates the multipart
boundary; do not manually set the `Content-Type` header.

| Form field | Required | Value |
| --- | --- | --- |
| `file` | Yes | The file to upload. In curl, prefix the local path with `@`. |
| `original_filename` | Yes | Original filename, up to 256 characters; used when downloading. |
| `slug` | Yes | Nonempty client-supplied string, up to 256 characters. A UUID is suitable. This is a required legacy field; use the returned `id` to identify submissions. |
| `stt` | Yes | Numeric STT ID supplied by TDP. |
| `year` | Yes | Reporting year as an integer, for example `2026`. |
| `quarter` | Yes | `Q1`, `Q2`, `Q3`, or `Q4`. |
| `section` | Yes | Exact, case-sensitive section name from the table below. |
| `ssp` | Yes | `true` for SSP-MOE; `false` for other programs. Always send explicitly. |
| `is_program_audit` | No | `true` for Program Integrity Audit; defaults to `false`. |
| `extension` | No | File extension metadata without the dot; defaults to `txt`. Set appropriately, especially for FRA. Validation also checks the uploaded filename. |

For quarterly TANF/SSP reporting, fiscal `Q1` covers October–December of the
previous calendar year, `Q2` January–March, `Q3` April–June, and `Q4` July–September.
For example, FY 2026 Q1 covers October–December 2025. Confirm the reporting period
with TDP for your program.

| Program | `section` | Upload notes |
| --- | --- | --- |
| TANF, SSP-MOE, Tribal TANF | `Active Case Data`, `Closed Case Data`, `Aggregate Data`, or `Stratum Data` | Use a section available for your program. Supported filename extensions include `.txt`, `.ms` followed by two digits, and `.ts` followed by two or three digits; case-insensitive. |
| FRA | `Work Outcomes of TANF Exiters`, `Secondary School Attainment`, or `Supplemental Work Outcomes` | `.csv` or `.xlsx`; requires FRA access (or OFA System Admin), `ssp=false`, and an active submission year. |
| Program Integrity Audit | Applicable TANF/Tribal section above | Set `is_program_audit=true` and `ssp=false`; the feature must be enabled and the year supported. |

The API derives the reporting program from `ssp`, your STT type, and the section;
`program_type` is a response field. Do not prefix section names with program names.
FRA submissions for years closed to submission return `400` with
`FRA submissions for this fiscal year are read-only.` Previously submitted files
can still be listed and downloaded subject to your permissions.

Example: upload a TANF Active Case Data file. Replace the path, filename, and
example slug; use a new slug for each submission (Python 3's
`python3 -c 'import uuid; print(uuid.uuid4())'` can generate a UUID).

```bash
curl --silent --show-error --fail-with-body \
  --request POST "$API_BASE_URL/v1/data_files/" \
  --header "Authorization: Bearer $ACCESS_TOKEN" \
  --header 'Accept: application/json' \
  --form 'file=@/path/to/tanf-q1.txt' \
  --form-string 'original_filename=tanf-q1.txt' \
  --form-string 'slug=893b12d5-883c-4302-b8cf-396c34b1cb10' \
  --form-string "stt=$STT_ID" \
  --form-string "year=$REPORT_YEAR" \
  --form-string "quarter=$REPORT_QUARTER" \
  --form-string 'section=Active Case Data' \
  --form-string 'ssp=false' \
  --form-string 'is_program_audit=false' \
  --form-string 'extension=txt' \
  --output submission.json \
  --write-out 'HTTP %{http_code}\n'
```

`--fail-with-body` needs curl 7.76 or newer. With older curl, omit that option,
check the printed HTTP status, and inspect the response before continuing.

Success is HTTP `201`. Save the returned `id` and `version`. The following is an
abbreviated example; other fields are also returned:

```json
{
  "id": 456,
  "original_filename": "tanf-q1.txt",
  "stt": 123,
  "year": 2026,
  "quarter": "Q1",
  "section": "Active Case Data",
  "program_type": "TAN",
  "version": 1,
  "is_program_audit": false,
  "has_error": false,
  "summary": null,
  "latest_reparse_file_meta": null
}
```

The response does not include the uploaded `file` bytes or the input `ssp` flag.
`user`, `version`, `program_type`, and lifecycle values are assigned by the server.
The file is inspected for malware when scanning is enabled, then parsing is
queued. **`201` means the upload was accepted; it does not mean the reporting
data passed validation.** `summary` may initially be `null` or have status
`Pending`. List submissions later to check results.

Every successful repeated POST creates a new version for that STT, reporting
period, section, and audit category. These endpoints do not provide an idempotency
key. If the connection times out after sending a file, check the list before
retrying to avoid unintended versions. Security inspection failures return
`400`; the uploaded bytes are not saved and those failed rows are excluded from
list results.

## List submissions and check results

`GET /v1/data_files/?stt={stt}`

| Query parameter | Required | Meaning |
| --- | --- | --- |
| `stt` | Yes | Numeric STT ID. Always provide it, even if your account has an assigned STT. |
| `year` | No, except for audit queries | Filter by reporting year. Always provide it with `file_type=program-integrity-audit`. |
| `quarter` | No | Filter by `Q1`, `Q2`, `Q3`, or `Q4`. |
| `file_type` | No | Select the reporting category using the table below. |

| `file_type` value | Returned files |
| --- | --- |
| Omitted | TANF/Tribal TANF, excluding Program Integrity Audit; does not include SSP or FRA. |
| `ssp-moe` | SSP-MOE files. |
| `program-integrity-audit` | TANF/Tribal Program Integrity Audit files, if enabled for the requested year. |
| `Work Outcomes of TANF Exiters` | FRA files in this section. |
| `Secondary School Attainment` | FRA files in this section. |
| `Supplemental Work Outcomes` | FRA files in this section. |

Use these exact values. Unknown `file_type` values currently fall back to the
default TANF/Tribal category rather than returning a validation error.

```bash
curl --silent --show-error --fail-with-body --get \
  "$API_BASE_URL/v1/data_files/" \
  --header "Authorization: Bearer $ACCESS_TOKEN" \
  --header 'Accept: application/json' \
  --data-urlencode "stt=$STT_ID" \
  --data-urlencode "year=$REPORT_YEAR" \
  --data-urlencode "quarter=$REPORT_QUARTER" \
  --output submissions.json
```

To list SSP-MOE files, add `--data-urlencode 'file_type=ssp-moe'` to this command.
For FRA, use, for example,
`--data-urlencode 'file_type=Work Outcomes of TANF Exiters'`; URL encoding is
necessary for the spaces.

The response is a **JSON array**, newest `created_at` first, with no pagination
wrapper or page parameters. No matches returns `[]`. Older submitted versions
are included; do not assume the first item is the only version or section.
Match the saved `id` from your upload to track that specific submission.

Abbreviated example after processing:

```json
[
  {
    "id": 456,
    "original_filename": "tanf-q1.txt",
    "stt": 123,
    "year": 2026,
    "quarter": "Q1",
    "section": "Active Case Data",
    "program_type": "TAN",
    "version": 1,
    "has_error": true,
    "state": "parsed_with_errors",
    "state_display": "Parsed with errors",
    "allowed_next_states": ["reparse_requested", "parse_started", "completed", "canceled"],
    "summary": {
      "status": "Accepted with Errors",
      "case_aggregates": null,
      "datafile": 456
    }
  }
]
```

`summary.status` describes the parser result:

| Status | Interpretation |
| --- | --- |
| `Pending` | Validation is not finished. |
| `Accepted` | Accepted without reported parsing errors. |
| `Accepted with Errors` | Accepted with errors to review. |
| `Partially Accepted with Errors` | Some data was not accepted; review the error report. |
| `Rejected` | Rejected during validation; review the error report. |

Treat a missing summary as unfinished processing. `has_error=false` alone is not
proof that processing is complete. Poll at a modest interval, such as 30 seconds,
with a timeout appropriate for your workflow. If processing fails or remains
pending, contact support with the DataFile ID and reporting period.

### Lifecycle response fields

`state` is the machine-readable lifecycle state, while `state_display` is its
human-readable label. Possible states include `uploaded`, `virus_scan_started`,
`virus_scan_failed`, `virus_scan_completed`, `reparse_requested`, `parse_started`,
`parse_failed`, `parsed_with_errors`, `parse_completed`, `stuck`, `completed`, and
`canceled`. They describe processing progress separately from `summary.status`.

`allowed_next_states` lists valid lifecycle transitions in a stable order;
`completed` and `canceled` are terminal and return an empty list. These three
fields are read-only. They do not grant an API caller permission to change state,
and the four operations in this guide do not provide a state transition API.
Unexpected stored state values are returned as stored, with an empty
`allowed_next_states` list. Transition history is not included in these responses.
See Swagger's `DataFile` schema for the full response fields.

## Download the submitted file

`GET /v1/data_files/{id}/download/`

Set `DATAFILE_ID` to the ID from your submission or list response:

```bash
export DATAFILE_ID='456'
curl --silent --show-error --fail \
  "$API_BASE_URL/v1/data_files/$DATAFILE_ID/download/" \
  --header "Authorization: Bearer $ACCESS_TOKEN" \
  --output downloaded-submission.txt \
  --write-out 'HTTP %{http_code}\n'
```

On `200`, the response contains the original submitted file bytes for that
DataFile version. Choose an output name and extension matching the submission.
This endpoint does not require `stt`, `year`, or `quarter` query parameters;
access is checked against the identified file. It does not return JSON or a
public storage URL. Regional Staff cannot download original submissions.

## Download the parsing error report

`GET /v1/data_files/{id}/download_error_report/`

Wait until processing has finished and a summary is available before requesting
the report. The endpoint generates a report if one has not yet been stored; it
is not a processing-status endpoint and does not return `202` to signal pending
processing.

```bash
curl --silent --show-error --fail \
  "$API_BASE_URL/v1/data_files/$DATAFILE_ID/download_error_report/" \
  --header "Authorization: Bearer $ACCESS_TOKEN" \
  --output error-report.xlsx \
  --write-out 'HTTP %{http_code}\n'
```

On `200`, save the binary response as `.xlsx` and open it with an Excel-compatible
spreadsheet application. The report describes errors for that submission; use it
to correct the source file, then create a new submission. No STT query parameter
is required. Access is checked against the identified file and your role.

## Handle errors and retries

API errors usually contain JSON with a `detail` message or a field name mapped
to validation messages. For example, a missing required `stt` filter returns
`400` with `{"stt": ["This field is required."]}`. Read the HTTP status before
treating an output file as a successful response.

| HTTP status | Meaning and next step |
| --- | --- |
| `400` | Correct missing/invalid fields, unsupported extensions, unavailable programs/years, or a failed security inspection. Review the message before resubmitting. |
| `401` | A supplied bearer token is expired or invalid. Refresh or sign in again; verify issuer, client, and audience if a new token fails. |
| `403` | Missing authentication can return this status; otherwise check account approval, role, STT/region, and operation permissions. A new token does not fix missing permissions. |
| `404` | The requested DataFile ID does not exist at that URL. Check the environment and ID. |
| `415` | Upload body has an unsupported media type. Use multipart form data. |
| `429` | Request rate exceeded. Honor `Retry-After` and slow down. The configured default is 300 requests/minute per client and user; deployments may override it. |
| `5xx` | Server/processing failure. Retry reads with backoff; check the list before retrying an upload whose outcome is uncertain. Contact support if it persists. |

For downloads, `curl --fail` prevents HTTP error bodies from being saved as a
spreadsheet or submission. Check curl's exit status as well: a network failure
can leave an incomplete output file. Do not consume it unless the command
succeeded. For production integrations, capture status codes and safe diagnostic
messages without logging tokens or reporting data. Contact
[TDP support](mailto:tanfdata@acf.hhs.gov) with the operation, DataFile ID if known,
time, status, and sanitized error message.

## Additional reference: parser logs

Authorized users can download parser logs with
`GET /v1/data_files/{id}/logs/` using the same bearer header. The response is plain
text; `404` means no log was found. Access follows the API's account approval,
model permissions, and STT/region checks. See the environment's Swagger reference
for this additional operation.
