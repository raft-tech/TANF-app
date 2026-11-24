# Backend Context

This context covers the Django API, Python backend code, Celery workers, parsing orchestration, backend tests, and backend deployment assets under `tdrs-backend/`.

## Boundaries

- API behavior and backend application logic live here.
- Celery worker behavior and asynchronous jobs live here.
- Backend parsing orchestration lives here, even when parser implementation details are delegated to another service.
- Authentication integration touches this context, but Keycloak-specific configuration and deployment details are documented in `tdrs-backend/keycloak/CONTEXT.md`.
- PLG observability configuration is documented in `tdrs-backend/plg/CONTEXT.md`.

## Test Strategy

- Backend unit and API integration tests live under `tdrs-backend/tdpservice/**/test/` and run with `pytest` (`task backend-pytest`).
- Global fixtures and role-specific users (`data_analyst`, `regional_user`, `ofa_admin`, `ofa_system_admin`, `digit_team`, `stt`, `other_stt`) are defined in `tdrs-backend/tdpservice/conftest.py`.
- Live Django-to-Go parser integration tests live in `tdrs-backend/tdpservice/parsers/test/integration/` and run separately via `task backend-pytest-go-integration`.
- Prefer direct serializer/model/service unit tests for validation permutations, test RBAC endpoints using 3 boundary cases, pass existing `user` and `stt` fixtures to `DataFileFactory`, and mock external boundaries (`S3FileHandler`, `parser_task.parse.delay`, `ClamAVClient`, `KeycloakSyncClient`) using `mocker.patch` at the module where they are used.
- Read `docs/agents/testing.md` for full layer ownership rules and `pytest` mocking boilerplate.

## Read With

- Root `CONTEXT.md`
- `CONTEXT-MAP.md`
- `docs/agents/testing.md`
- Relevant technical docs under `docs/Technical-Documentation/`
- Relevant backend README or module-level docs near the code being changed
