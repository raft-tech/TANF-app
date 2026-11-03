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
task backend-pytest PYTEST_ARGS="keycloak/test/test_readiness.py tdpservice/users/test/test_keycloak_realm_config.py -v"
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
jq versions, and config-cli artifact manifest. Retain the image and these
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
`runtime-packages.lock` pins jq and its package dependency versions; APT
verifies package hashes against signed repository metadata. Packages are fetched
from DHI's signed Debian repository; future unavailable pins must fail, not float.
Config-cli remains a separate tool, outside the server provider directory.
Config-cli is built from upstream revision
`90c97fc0f8968286400be7bcb27f8165581003f2` with `config-cli-security.diff`:
6.5.1-tdp-security.1, Spring Boot 3.5.16, Spring Framework 6.2.19, Jackson 2
BOM 2.21.8 and Jackson 3 BOM 3.2.4. The patch also removes an upstream duplicate
SnakeYAML declaration rejected by Maven 3.10. The pinned DHI Maven/JDK 21 builder
runs 21 focused Java unit tests; no integration tests or Docker socket are used.
The generated SHA256, patched POM, source revision, dependency patch, and Surefire
reports are exported to each build's `config-cli-evidence/` directory. The JAR
and its checksum are checked against the final image. The upstream Keycloak
26.5.5 client/normalization pairing is retained: live compatibility with the
26.8.1 server is **not established**.

Curl and its dependency closure are removed. Readiness uses a bounded loopback
HTTP helper (3-second overall timeout, 2-second status-line timeout, HTTP/1.0 or
1.1 status 200 only). Fourteen unit cases use synthetic peers, not a real server.

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

## Latest remediation snapshot — 2026-11-03

**Still blocked:** both final security candidates build and pass offline checks,
but each raw scan reports **0 Critical / 3 High / 44 Medium / 26 Low**. All
remaining blocking reports are OS packages; there are no Java Critical/High
reports. See [TRIAGE.md](TRIAGE.md) for the exact three advisories and why the
authentic vendor VEX was not applied automatically. The zero-Critical/High gate
has not been weakened. No candidate is approved for release.

| Platform | Local immutable image ID (SHA256) | Build evidence | Scan/SBOM evidence |
| --- | --- | --- | --- |
| arm64 | `02680f22bc3ec59b5ef516f085bd2aa112f303fa70e64b6ef3ae63efd74ebef9` | `results/build-20261103T185903Z-44390` | `results/scan-20261103T185934Z-44789` |
| amd64 (emulated) | `91fb627b05a9800d85fd2091e05f934f45342c105b8b19eb5e220ab78e438d96` | `results/build-20261103T185903Z-44391` | `results/scan-20261103T190030Z-45432` |

Actual versions: Keycloak 26.8.1, Temurin Java 21.0.13+9-LTS, nginx 1.30.6,
jq 1.8.2, config-cli 6.5.1-tdp-security.1. Both config-cli JARs and exported
checksums match SHA256
`00c6359800f2f2273ed43ae2b311fb88236916c9cc82bff2fcd0aea881f28f96`.
Each build exports 21 passing focused Java test results. Final pytest:
**30 passed, 0 failed/skipped, 2 existing warnings in 3.44s**; Flake8 and shell
lint passed. An earlier test run exposed an incorrect assumption that one TCP
`recv` returns all headers; the synthetic peer now reads through the header
terminator. The rerun passes without changing the helper's behavior.

Changes remain uncommitted for manual review. No smoke tests, runtime acceptance,
publication, deployment, or Phase 3 work were performed. Existing service images
were not replaced by these candidates. The test/lint tasks' existing `backend-up`
dependency did start supporting Compose services; it is not candidate validation.

## Historical Phase 2 review snapshot — 2026-11-03, before remediation

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

The original candidate Critical finding was `CVE-2026-84939` in the server's FreeMarker
2.3.32 JAR (scanner reports 2.3.35 fixed). High findings include server Java/OS
dependencies and config-cli's Spring/Jackson dependencies. All remain blocking;
none are waived or suppressed. TDP image maintainers must coordinate remediation
with DHI/upstream config-cli maintainers and security reviewers. Next decisions:
authorize investigation of a newer verified server base and/or pinned config-cli
source/dependency rebuild, then rebuild and rescan both architectures. Do not
replace internal server JARs ad hoc or interpret potential vendor-version false
positives as accepted risk without evidence/security disposition.
