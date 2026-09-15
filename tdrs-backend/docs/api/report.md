# Data file metadata

DataFile requests retain the existing string-based API contract. Internally, each
DataFile is classified by one canonical Section relationship. The `section` and
`program_type` response fields are string projections of that relationship rather
than independent classification values.

## Upload

`POST /v1/data_files/` uses `multipart/form-data` with these fields:

- `file`: The file to upload.
- `original_filename`: The original filename.
- `slug`: The frontend-generated UUID used for storage.
- `extension`: The file extension.
- `user`: The uploading user's UUID.
- `stt`: The submitting STT ID.
- `year`: The reporting year.
- `quarter`: One of `Q1`, `Q2`, `Q3`, or `Q4`.
- `section`: The Section name, such as `Active Case Data`.
- `ssp`: Whether the submission is for SSP.
- `is_program_audit`: Whether the submission is a Program Integrity Audit.

The backend combines `section`, `ssp`, and the STT type to resolve the canonical
Program and Section. TANF, SSP, and Tribal TANF may share Section names, so a
Section name alone is not used as canonical identity. Program Integrity Audit is
supported only for TANF and Tribal TANF Sections.

A successful upload returns `201 Created`. The response preserves the existing
scalar fields, including:

```json
{
  "id": 123,
  "original_filename": "active-case.txt",
  "slug": "f6ccc39e-7d1a-11eb-9439-0242ac130002",
  "extension": "txt",
  "user": "ee3c5c3a-7d15-11eb-9439-0242ac130002",
  "stt": 15,
  "year": 2026,
  "quarter": "Q1",
  "section": "Active Case Data",
  "program_type": "TAN",
  "is_program_audit": false,
  "version": 1
}
```

The temporary internal field name `section_ref` is not exposed.

## List and retrieve

- `GET /v1/data_files/?stt={id}` returns the existing bare JSON array without a
  pagination envelope.
- Optional list filters are `year`, `quarter`, and `file_type`.
- `file_type=ssp-moe` selects SSP files.
- `file_type=program-integrity-audit` selects Program Integrity Audit files when
  the feature is enabled and the requested year is supported.
- FRA `file_type` values are canonical FRA Section names.
- Other `file_type` values retain the existing TANF and Tribal TANF behavior.
- `GET /v1/data_files/{id}/` retrieves one DataFile.
- `GET /v1/data_files/{id}/download/` downloads the submitted file.

List and retrieve responses continue returning string `section` and
`program_type` fields derived from the canonical Section and Program.
