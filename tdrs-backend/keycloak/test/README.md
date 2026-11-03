# Keycloak image build and security evidence

The user removed the automated smoke-test requirement on 2026-11-03.
This directory retains local build/version/provenance and security tooling, not
startup/import smoke tests. Phase 2 candidates are not approved releases.

## Prerequisites and commands

From the repository root, use Docker with Buildx, Task, and Python 3.10+.
The unchanged image requires linux/amd64 execution (emulated on Apple Silicon)
because it downloads amd64-only utilities. No ARM64 baseline is established.
Candidate builds use native architecture DHI packages and support both platforms.
Authenticate with `docker login dhi.io` before building. A read-only Docker access
token is sufficient; never put tokens into build arguments or checked-in files.

```bash
# Retain the existing baseline: do not rebuild that tag from the migrated Dockerfile.
BUILDX_BUILDER=colima task keycloak:build IMAGE_REF=tdp-keycloak:dhi-candidate-amd64 PLATFORM=linux/amd64
BUILDX_BUILDER=colima task keycloak:build IMAGE_REF=tdp-keycloak:dhi-candidate-arm64 PLATFORM=linux/arm64
task keycloak:scan IMAGE_REF=tdp-keycloak:baseline PLATFORM=linux/amd64
task keycloak:scan IMAGE_REF=tdp-keycloak:dhi-candidate-amd64 PLATFORM=linux/amd64
task keycloak:scan IMAGE_REF=tdp-keycloak:dhi-candidate-arm64 PLATFORM=linux/arm64
task backend-pytest PYTEST_ARGS="tdpservice/users/test/test_keycloak_realm_config.py -v"
task backend-lint
task keycloak:lint
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

## Candidate checks and security gate

All external Dockerfile stages are version/digest-pinned DHI Debian 13 images.
The final non-dev Keycloak runtime retains Java 21, CA trust, and its existing
libraries/loader. Only missing shared libraries are copied from the compatible
assembly stage; libc is never transplanted. The final user is `65532:65532`.
`runtime-packages.lock` pins curl/jq and their package dependency versions; APT
verifies package hashes against signed repository metadata. Packages are fetched
from DHI's signed Debian repository; future unavailable pins must fail, not float.
Config-cli remains a separate tool, outside the server provider directory.
The upstream 6.5.1 / 26.5.5 release JAR is SHA256-verified; retaining that existing
version pairing is not proof of live compatibility with Keycloak 26.7.3.

Build checks execute binaries offline on the requested architecture, verify the
JAR/copied-file hashes, required utilities, non-root UID/writable paths, absence
of package/build tools, and nginx configuration syntax. They do not start servers.
Package inventory and copied-file checksums are retained under
`/usr/share/keycloak-image/`; `assembly-packages.tsv` describes the assembly stage,
not an assertion that all its packages are included in the final image.

`keycloak:scan` pins Trivy 0.76.1 by digest and scans an archive of the resolved
local image ID without a Docker socket mount. It checks the platform before
scanning and retains image metadata/archive, full OS/Java vulnerability JSON,
CycloneDX SBOM, scanner/database timestamps, and logs under ignored `results/scan-*`.
Database downloads are shared in ignored `results/trivy-cache`; each completed
scan retains its own database metadata. Avoid concurrent scans against that cache.
**Any Critical or High finding fails the gate.** No unfixed/VEX/ignore filtering
is used. Review coverage in each report: unmanaged baseline binaries may not be
identified by package scanning, so baseline counts are not exhaustive.
No release acceptance can be inferred from DHI branding or a successful build.

## Phase 2 review snapshot — 2026-11-03

**Blocked, not accepted:** the approved gate requires zero Critical and High
findings. No smoke tests, publication, deployment, or manual runtime validation
were performed. The baseline tooling is committed at `12c0310f6`; candidate
sources remain uncommitted for manual review.

| Image | Platform | Local immutable ID (SHA256) | Build/offline checks | Critical / High |
| --- | --- | --- | --- | --- |
| Retained baseline | amd64 | `97bb13701e2504588244a092739a3fc18782bc63fc1c5c7554a7d5f2b7380ff7` | Historical build passed; no runtime baseline | 5 / 44 |
| DHI candidate | amd64, emulated | `24ad74e12ac7ad83716b3cb0dafa10f029f59bf6adcec3154773a18d45274dd5` | Passed | 1 / 41 |
| DHI candidate | arm64, native | `97d75a3b6b40f8d395cf775b0a4d8ade114c47585e8fe17715bc9beefd632369` | Passed | 1 / 41 |

Final local build evidence: `results/build-20261103T181935Z-33208` (amd64) and
`results/build-20261103T181932Z-33170` (arm64). Complete scan/SBOM evidence:
`results/scan-20261103T181425Z-30165` (baseline),
`results/scan-20261103T182048Z-33927` (amd64), and
`results/scan-20261103T181959Z-33522` (arm64).
Trivy DB updated 2026-11-03 13:13:42 UTC; Java DB updated 01:08:45 UTC.
Realm regression: **16 passed**, two existing Django deprecation warnings.
Backend Flake8 and `keycloak:lint` passed.

The candidate Critical finding is `CVE-2026-84939` in the server's FreeMarker
2.3.32 JAR (scanner reports 2.3.35 fixed). High findings include server Java/OS
dependencies and config-cli's Spring/Jackson dependencies. All remain blocking;
none are waived or suppressed. TDP image maintainers must coordinate remediation
with DHI/upstream config-cli maintainers and security reviewers. Next decisions:
authorize investigation of a newer verified server base and/or pinned config-cli
source/dependency rebuild, then rebuild and rescan both architectures. Do not
replace internal server JARs ad hoc or interpret potential vendor-version false
positives as accepted risk without evidence/security disposition.
