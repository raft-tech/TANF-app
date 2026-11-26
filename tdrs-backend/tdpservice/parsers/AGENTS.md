# AGENTS.md (Parsers & Parsing Orchestration)

Rules specific to parsing orchestration and parser tests under `tdrs-backend/tdpservice/parsers/`. For repo-wide testing rules and Go parser context, see `docs/agents/testing.md` and `tdrs-services/parser/CONTEXT.md`.

## Parser Testing Boundaries

- New TANF/SSP/Tribal/FRA record decoders, field transformers, validators, and batch writers belong in the Go parser (`tdrs-services/parser/internal/**` via `make test`), not only in the deprecated Python parser.
- Live Django-to-Go parser integration tests belong in `tdrs-backend/tdpservice/parsers/test/integration/` and run via `task backend-pytest-go-integration` against real Celery (`go-parser` queue), Postgres, Redis, and LocalStack containers.
- Eager Celery task execution only proves synchronous behavior; use the real `go-parser` integration suite when verifying asynchronous delivery, retries, duplicate processing, stale-worker protection, or worker visibility of committed data.
- Do not parse multi-thousand-record files (`big_file`, `ssp_section1_datafile`) in unit tests that only check task scheduling, backups, or line-1 headers.
