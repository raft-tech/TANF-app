# Keycloak baseline build evidence

The user removed the automated smoke-test requirement on 2026-11-03.
This directory retains the local build/version/provenance tooling only.

## Prerequisites and commands

From the repository root, use Docker with Buildx, Task, and Python 3.10+.
The unchanged image requires linux/amd64 execution (emulated on Apple Silicon)
because it downloads amd64-only utilities. No ARM64 baseline is established.

```bash
task keycloak:build IMAGE_REF=tdp-keycloak:baseline PLATFORM=linux/amd64
task backend-pytest PYTEST_ARGS="tdpservice/users/test/test_keycloak_realm_config.py -v"
task backend-lint
bash -n tdrs-backend/keycloak/test/build.sh
git diff --check
```

Run pytest with the repository `test` skill's separate tmux pane and lint with
the `lint` skill. The existing backend test/lint tasks call `backend-up`;
review that side effect before rerunning them.

On Colima, confirm available VM disk space with `colima ssh -- df -h /`.
If a stale custom Buildx builder fails while the built-in `colima` builder is
healthy, select it for just this build without changing the user's default:

```bash
BUILDX_BUILDER=colima task keycloak:build IMAGE_REF=tdp-keycloak:baseline PLATFORM=linux/amd64
```

`keycloak:build` loads a local image, never pushes it, and saves its build log
and Buildx metadata (including resolved donor references where exposed by the
builder) under ignored `test/results/build-*`. It reports the source commit,
production-file diff, immutable local ID, platform, actual server/Java/nginx/
jq/curl versions, and config-cli artifact manifest. Retain the image and these
local artifacts; do not rebuild the baseline after migrating the Dockerfile.

## Verification boundary

A successful image build, version report, or backend regression run does not
prove successful startup, realm imports, authentication, persistence, supervision,
or Cloud.gov compatibility. Runtime and real Login.gov/AMS checks are deferred to
separately authorized integration/manual verification, not reported as passed.

The build wrapper removes only its own version-inspection container. Build
evidence and the baseline image are deliberately retained for comparison.
