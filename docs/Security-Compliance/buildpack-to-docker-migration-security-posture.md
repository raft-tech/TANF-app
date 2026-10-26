# Transitioning TDP Deployments from Cloud.gov Buildpacks to Docker Containers

## Security Posture & Compliance Analysis

**Prepared for:** ACF TDP Stakeholders
**Date:** April 2026
**Public-image proposal update:** October 26, 2026 — draft pending security-team approval
**Related Issues:** [Docker migration #5542](https://github.com/raft-tech/TANF-app/issues/5542), [public-image review #6176](https://github.com/raft-tech/TANF-app/issues/6176), [GHCR identities and Keycloak CI/CD #5980](https://github.com/raft-tech/TANF-app/issues/5980)

---

## Summary

This document evaluates whether moving TDP deployments from Cloud.gov-managed buildpacks to team-managed Docker images would **maintain or improve the current security posture** while addressing known operational limitations in the current deployment model.

- **Background on the original buildpack decision:** [ADR-011](../Technical-Documentation/Architecture-Decision-Record/011-buildpacks.md) documents that TDP leveraged Cloud.gov buildpacks in 2021 in part because they provided a faster path to ATO than the team's earlier DockerHub-based approach, which lacked sufficient security documentation for ACF review.
- **What is changing:** TDP would shift from Cloud.gov-managed buildpacks to Docker DHI hardened base images and TDP-managed Docker images for application deployment, while continuing to run the applications inside the same Cloud.gov platform and runtime environment.
- **Implementation status note:** The current repository Dockerfiles still reference standard public images in some base or final stages, including `python:3.10.8-slim-bullseye`, `node:22-alpine`, and `nginx:1.25-alpine`. The DHI-based security claims in this document should be treated as target-state controls until those image baselines are updated to approved DHI images or an equivalent approved hardened-image baseline is documented.
- **Why this is being considered now:** Buildpacks continue to create operational pain points, including long deploy times, repeated dependency downloads, less predictable build behavior, and limited visibility into the full runtime stack. At the same time, Docker image security capabilities and documentation have matured, especially around hardened base images, SBOMs, provenance, signing, and vulnerability management.
- **Security responsibility impact:** This change shifts responsibility for selecting approved base images, maintaining TDP's derived application images, and applying updated DHI releases into the deployment lifecycle from Cloud.gov to the TDP application team. It does **not** mean TDP becomes responsible for remediating CVEs in DHI base images themselves; that remediation remains with the DHI provider. TDP is responsible for rebuilding, validating, and redeploying downstream images after remediated base image versions are published. Based on the current architecture, this does **not** change the Cloud.gov hosting model or the ATO boundary, because the workloads would still run inside the same FedRAMP-authorized Cloud.gov environment and retain the same inherited platform controls.
- **Key tradeoffs:** The main tradeoff is greater operational and security ownership by the TDP team in exchange for better supply chain visibility, reproducibility, auditability, and deployment control. In practice, that means TDP must monitor for remediated DHI releases and update its derived images on an appropriate timeline, and ACF may need to evaluate whether Docker Hardened Images' enterprise tier or similar vendor support is needed if contractual remediation timelines such as a 7-day high/critical CVE response target are required.
- **Registry proposal:** TDP proposes distributing approved deployment images through GitHub Container Registry (GHCR) with **public, anonymous download access and authenticated, restricted publishing and replacement**. The existing security approval covers private images only; this document does not authorize a visibility change. Section 8.4 describes the proposed scope, publishing controls, sensitive-content checks, and evidence required for security review.
- **Scope and operational reason:** Keycloak is the first proposed candidate. The intended target model also covers TDP-managed application and base images as they move to approved hardened baselines, with readiness assessed per package. Public pulls would remove the dependency on expiring GHCR pull PATs during Cloud.gov restages; publishing still requires authorized credentials. The HHS robot-account request remains separate.
- **Compliance disposition:** The packaging change and proposed public artifact distribution are security relevant. Cloud.gov hosting and the application authorization boundary would remain unchanged, but image contents and metadata would become publicly downloadable. Update the SIA and targeted SSP narratives and obtain security-team approval before changing visibility. Built-image inspection evidence is still pending; the source review in this document is not a clean-image certification.

---

## 1. Current State: Buildpack Deployment Challenges

TDP currently deploys frontend and backend applications to Cloud.gov using standard buildpacks. While functional, this approach introduces:

| Challenge | Impact |
|-----------|--------|
| **Extended deployment times** | 15–30+ minute deployment windows |
| **Transient network failures** | Dependencies re-downloaded from scratch on every deploy, increasing failure risk |
| **Supply chain volatility** | Upstream package changes can introduce regressions without warning |
| **Environment inconsistency** | No guarantee of identical behavior across dev, staging, and production |
| **Limited control** | Inability to pin or audit the full dependency tree of the runtime environment |

---

## 2. Cloud.gov Security Controls: Inherited Regardless of Deployment Method

Cloud.gov holds **FedRAMP Moderate Authorization**, covering over 60% of the 323 NIST SP 800-53 Rev 5 controls at the infrastructure and platform level.

### 2.1 Control Inheritance Is Deployment-Method Agnostic

The following platform-level controls are **fully inherited by tenant applications regardless of whether buildpacks or Docker images are used**:

| Control Family | Cloud.gov Responsibility | Affected by Deployment Method? |
|----------------|--------------------------|-------------------------------|
| **Physical Security (PE)** | AWS GovCloud data centers | No |
| **Infrastructure Security** | AWS GovCloud services & configuration | No |
| **Platform Security** | Cloud Foundry, container runtime, networking | No |
| **Container Isolation** | garden-runc runtime with cgroups, process namespaces, user namespaces | No |
| **Network Security** | Platform networking, TLS termination, routing | No |
| **Continuous Monitoring** | FedRAMP continuous monitoring, annual assessments | No |
| **CM-2 (Baseline Config)** | Platform configuration baseline | No — platform portion unchanged |
| **AU-12 (Audit Generation)** | Platform event logging | No |

**Critical point:** Cloud.gov does not use Docker's runtime. All applications—whether deployed via buildpacks or Docker images—run under `garden-runc`, built on the Open Container Initiative's `runc` specification. Both deployment methods receive identical container isolation: cgroups for resource limiting, process namespaces for isolation, and user namespaces to prevent privilege escalation.

### 2.2 What Changes: The Shared Responsibility Shift

The primary compliance difference between buildpacks and Docker is **who maintains the base image layer**:

| Responsibility | Standard Buildpacks | Docker (with DHI) |
|----------------|--------------------|--------------------|
| OS-level patching | Cloud.gov (on restage) | TDP team via DHI automated patching |
| Language runtime updates | Cloud.gov | TDP team via Dockerfile version pinning |
| Dependency management | Re-downloaded each deploy (uncontrolled) | Locked in image layers (controlled, auditable) |
| Vulnerability scanning | Limited visibility | Full SBOM + automated CVE scanning |
| Configuration hardening | Opaque buildpack defaults | CIS-benchmarked, STIG-scanned base images |

This shift in responsibility is **not a net loss**—it is a trade of opaque, automatic updates for transparent, auditable, and controlled updates backed by industry-recognized security benchmarks.

---

## 3. Docker Hardened Images: Target Security Guarantees

Docker provides [CIS-validated Hardened Images](https://hub.docker.com/hardened-images/catalog) that are **free to use, share, and build on** under the Apache 2.0 license.

The guarantees below apply only if the approved production image baseline uses DHI images, or an alternative hardened-image source with equivalent documented controls. If the final implementation continues to use standard public images, the SIA and SSP should either document compensating controls or avoid claiming DHI-specific benefits such as CIS validation, SLSA provenance, signed SBOMs, VEX statements, or DHI remediation timelines.

### 3.1 Community Tier (Free) — Security Features

| Feature | Detail |
|---------|--------|
| **Near-zero CVEs** | Continuously scanned and patched to maintain minimal known exploitable vulnerabilities |
| **CIS Benchmark Compliance** | Images validated against CIS Docker Benchmark v1.8.0 |
| **Distroless Variants** | Reduce attack surface by up to 95% compared to standard images |
| **Non-root Execution** | Default least-privilege configuration (FIPS & STIG variants only) |
| **SLSA Build Level 3 Provenance** | Tamper-resistant, verifiable build chain |
| **Signed SBOMs** | Complete Software Bill of Materials for every component |
| **VEX Statements** | CVE exploitability context for accurate risk assessment |
| **Cryptographic Signatures** | Every package and image cryptographically signed and verified |
| **Source-built Packages** | Built from upstream source by Docker, not pulled from third-party repos |
| **Automatic Patching** | Rebuilt when upstream security updates are available |

### 3.2 Enterprise Tier (Available if Needed)

| Feature | Detail |
|---------|--------|
| **7-day CVE SLA** | Critical/high severity vulnerabilities remediated within 7 days |
| **FIPS-enabled Variants** | For cryptographic module compliance |
| **STIG-ready Images** | Meet Department of Defense security requirements |
| **Custom Modifications** | Tailored images for specific compliance needs |
| **Extended Lifecycle Support** | Post-EOL security patches |

### 3.3 How DHI Compares to Buildpack Security

| Security Dimension | Buildpacks | Docker Hardened Images |
|--------------------|-----------|----------------------|
| **Vulnerability visibility** | Limited; opaque stack | Full SBOM with every component listed |
| **CIS compliance** | Not CIS-benchmarked | CIS Benchmark v1.8.0 validated |
| **Supply chain integrity** | Dependencies fetched at deploy time from public repos | SLSA Level 3 provenance, cryptographic signatures |
| **Attack surface** | Full OS with all default packages | Distroless variants reduce surface by up to 95% |
| **Patch transparency** | Automatic but opaque; requires restage | Automatic with full audit trail |
| **Runtime privilege** | Varies by buildpack | Non-root by default |
| **Audit artifacts** | None provided | SBOMs, VEX statements, provenance attestations |

---

## 4. NIST SP 800-53 Control Mapping

The following table maps relevant NIST controls to how they are addressed under the proposed Docker deployment model:

| Control | Description | How Addressed |
|---------|-------------|---------------|
| **CM-2** | Baseline Configuration | CIS-benchmarked DHI base images provide a documented, hardened baseline |
| **CM-6** | Configuration Settings | Dockerfile and image layers provide version-pinned, reproducible configuration |
| **CM-7** | Least Functionality | Distroless DHI variants eliminate unnecessary packages and services |
| **RA-5** | Vulnerability Scanning | DHI continuous scanning + CI/CD pipeline scanning (e.g., Trivy, Grype) |
| **SA-10** | Developer Configuration Management | SLSA Level 3 provenance ensures tamper-resistant build pipeline |
| **SA-11** | Developer Testing & Evaluation | Automated security scanning integrated into image build process |
| **AC-3 / AC-6** | Access Enforcement / Least Privilege | Proposed anonymous image reads; package write/admin permissions and CI publishing credentials limited to authorized identities (Section 8.4) |
| **CM-3** | Configuration Change Control | Review image composition and publishing workflow changes; approve public visibility and record the released digest and supporting checks |
| **SI-2** | Flaw Remediation | DHI automatic patching; Enterprise tier offers 7-day SLA |
| **SI-7** | Software & Information Integrity | Cryptographic signatures on all images and packages |
| **SC-28** | Protection of Information at Rest | Cloud.gov runtime/data protections remain inherited; proposed public registry artifacts must contain no secrets or sensitive data (Section 8.4) |
| **AU-12** | Audit Record Generation | SBOMs and provenance attestations provide audit artifacts not available with buildpacks |

---

## 5. Addressing the "Not Recommended" Caveat in Cloud.gov Docs

Cloud.gov's Docker deployment documentation notes that Docker is "not a recommended path" and that users "lose a large set of features." This language warrants context:

1. **The caveat is about operational convenience, not security.** Cloud.gov recommends buildpacks because they reduce the maintenance burden on tenants. With DHI's automated patching and CI/CD integration, this burden is manageable and well-understood.

2. **The "lost features" are buildpack-specific automation.** Specifically, automatic language runtime updates on restage. With Docker, we gain explicit control over when and how these updates occur—improving change management (CM-3) and reducing the risk of unplanned regressions.

3. **Cloud.gov fully supports Docker deployments.** The `cf push --docker-image` workflow is a first-class deployment method. The same `garden-runc` container runtime, the same network isolation, and the same platform security controls apply.

---

## 6. Operational Security Improvements

Beyond maintaining compliance, Docker deployments actively improve our security operations:

### 6.1 Immutable, Versioned Artifacts

Each deployment uses a specific, tagged image digest. If a vulnerability is discovered, we can identify exactly which deployments are affected and roll back to a known-good image instantly.

### 6.2 Reproducible Builds

The same image runs in development, staging, and production. Environment-specific bugs are eliminated, reducing the risk of security issues that only manifest in production.

### 6.3 Supply Chain Control

Dependencies are locked at build time, not fetched from public repositories during each deployment. This eliminates an entire class of supply chain attacks where a compromised upstream package could be pulled into production during a routine deploy.

### 6.4 Enhanced Auditability

SBOMs, provenance attestations, and VEX statements provide audit artifacts that buildpack deployments simply cannot produce. This strengthens our posture for RA-5 (Vulnerability Scanning) and AU-12 (Audit Generation).

---

## 7. Proposed Mitigation Strategy

To address the additional responsibilities that come with Docker deployment, we propose:

| Responsibility | Mitigation |
|----------------|------------|
| **Base image maintenance** | Use DHI images with automated patching; pin to specific digests in CI/CD |
| **OS-level security updates** | DHI continuous scanning and automatic rebuilds on upstream updates |
| **Vulnerability management** | Integrate container scanning (e.g., Grype) into CI/CD pipeline for TDP frontend/backend containers; block deployment on critical/high CVEs |
| **Configuration hardening** | Use DHI or an approved equivalent hardened-image baseline; document any compensating controls if standard public base images remain in use |
| **Sensitive-content disclosure** | Inspect image configuration, history, every distributed layer, and attached metadata before public release; block publication on unresolved sensitive findings and scan every subsequent build (Section 8.4) |
| **Unauthorized publishing/replacement** | Limit package write/admin and CI secret access; protect release refs and publishing workflows; deploy reviewed digests rather than trusting mutable tags (Section 8.4) |
| **Continuous monitoring** | Feed container scanner results, GHCR package activity, image digest changes, and DHI/base image update status into the existing process for monthly and quarterly reporting |
| **POA&M and vulnerability reporting** | Track unresolved high/critical container findings, scanner exceptions, overdue base image updates, and accepted residual risks through the applicable ACF/TDP vulnerability management process, including POA&M tracking where required |
| **Incident response** | Detect, triage, contain, and recover from image-related events using scanner alerts, CircleCI job logs, GHCR package activity, image digest inventory, and redeployment of a known-good digest |
| **SSP documentation updates** | Update relevant control narratives to reflect Docker deployment model and DHI security features |

---

## 8. Compliance Review/Updates

ACF feedback correctly identifies the Docker migration as a security-relevant modification even though application hosting, the application authorization boundary, and runtime application data flows would remain unchanged. Public image distribution adds an external artifact-disclosure path that must be evaluated separately. The existing private-image approval does not cover that change; the proposed compliance package should include an updated SIA, targeted SSP updates, and image-inspection evidence.

### 8.1 SIA and SSP Updates

The SIA should evaluate the packaging change as a significant security-relevant modification and document:

- No change to the system authorization boundary, Cloud.gov hosting environment, or application data flows
- New or changed implementation details for Docker image build, registry storage, scanning, signing/provenance, and deployment
- TDP responsibility for derived application images and base image update adoption
- Cloud.gov responsibility for the platform runtime, host operating system, network isolation, and inherited FedRAMP controls
- Residual risks associated with GHCR, external base image dependency, image tag/digest management, and delayed vulnerability remediation
- The change from restricted image downloads to anonymous public downloads, the package-by-package rollout scope, and the fact that publicly downloaded artifacts cannot reliably be recalled
- Inspection results tied to exact image digests, ongoing sensitive-content checks, and restrictions on publishing, tag replacement, package administration, and CI credentials (Section 8.4)

### 8.2 Continuous Monitoring, Vulnerability Reporting, and POA&M

Container vulnerability management should be integrated into the existing continuous monitoring (ConMon) process rather than treated as a standalone CI/CD activity.

| Activity | Proposed Documentation Update |
|----------|-------------------------------|
| **CI/CD scanning** | Document vulnerability and sensitive-content checks for every in-scope image during build and before publication or deployment, including Keycloak and later hardened application/base images |
| **Recurring review** | Include container scanner findings, GHCR package activity, image inventory, and base image update status in monthly and quarterly ConMon reporting |
| **Vulnerability reporting** | Report high/critical image findings using the same severity, ownership, due date, and remediation evidence practices used for existing vulnerability sources |
| **POA&M integration** | Open or update POA&M items for overdue remediation, accepted residual risk, scanner exceptions, or findings that cannot be remediated within required timelines |
| **Evidence artifacts** | Retain redacted scan results, SBOMs, image digests, GitHub Actions/CircleCI workflow and job records, release tags, permission-review records, and remediation validation as audit evidence; restrict raw findings that could contain secrets or sensitive data |

### 8.3 Configuration Management: CM-2 and CM-6

Docker configuration artifacts are stored in the TANF-app GitHub repository and should be treated as version-controlled configuration baseline artifacts.

| Artifact | Repository Location | CM Relevance |
|----------|---------------------|--------------|
| Backend application image | `tdrs-backend/Dockerfile` | Defines backend deployment image composition |
| Backend base image | `tdrs-backend/Dockerfile.base` | Defines backend base runtime and OS package baseline |
| Frontend application image | `tdrs-frontend/Dockerfile` | Defines frontend deployment image composition |
| Frontend base image | `tdrs-frontend/Dockerfile.base` | Defines frontend build/runtime baseline |
| Keycloak image | `tdrs-backend/keycloak/Dockerfile` | Defines Keycloak container image baseline, where applicable |
| Admin console image | `tdp-admin/Dockerfile` | Defines Next.js local-development, build, and runtime stages |
| Go parser image | `tdrs-services/parser/Dockerfile` | Defines compiled parser binary and runtime configuration |
| Build-context exclusions | `.dockerignore` files in backend, frontend, admin, and parser directories | Control which local files enter their respective build contexts; must be reviewed alongside `COPY` instructions |
| Current GHCR release publisher | `.github/workflows/publish-release-image.yml` | Builds and pushes backend/frontend version and `latest` tags using the job's `GITHUB_TOKEN` |
| CircleCI build/deployment configuration | `.circleci/config.yml`, `.circleci/deployment/workflows.yml`, `.circleci/deployment/jobs.yml`, `.circleci/deployment/commands.yml` | Defines deployment orchestration and should define image build, tag, authentication, and publish process when Docker image publishing is moved into CircleCI |

The SSP should state that Dockerfile changes, build-context exclusions, base image version changes, GitHub Actions/CircleCI deployment or image-publishing configuration changes, package permission/visibility changes, and production image digest changes are configuration-controlled changes subject to code review, CI validation, release approval, and audit retention.

### 8.4 GHCR ATO Considerations

GHCR introduces an external registry dependency and should be documented explicitly in the SSP, implementation architecture, and SIA. **The following is a proposal pending security-team approval, not a statement that these controls are all implemented or that any image has passed inspection.**

| Area | Required Documentation |
|------|------------------------|
| **External dependency and downloads** | Proposed GHCR packages would allow anyone to download image layers, configuration, and publicly attached metadata without authentication. This grants no access to running Cloud.gov apps, databases, or runtime secrets |
| **Publishing and administration** | Uploading images or repointing tags requires an authenticated identity with package write access. Deletion, visibility changes, and permission management require appropriate package administration rights. Limit both direct grants and inherited repository/team access |
| **Authentication method** | Prefer the job-scoped `GITHUB_TOKEN` for authorized GitHub Actions publishing. If CircleCI publishes, use an approved machine identity and classic PAT with the necessary package scope, stored in a restricted context and managed through the existing secret-management process. Public pulls need no GHCR PAT |
| **Logging and monitoring** | Retain and review GitHub Actions/CircleCI job records, package publishing events, permission/visibility changes, CI credential/context changes, and available GitHub/GHCR audit events. Do not assume anonymous downloads provide a complete reader audit trail |
| **Image integrity** | Record and deploy the reviewed immutable digest; tags, including version tags and `latest`, can be replaced by an authorized writer. Signing/provenance and deployment verification are target controls to implement and validate, not protections conferred by public visibility |
| **Retention and recovery** | Release image tags and digests should be retained long enough to support rollback, forensic review, and audit evidence needs |

#### 8.4.1 Proposed Scope and Rollout

The proposed target policy applies to **all TDP-managed deployment and base images**, beginning with Keycloak and extending to the remaining images as they move to approved DHI or equivalent hardened baselines. This is a proposed scope for stakeholder/security confirmation, not blanket approval to expose every current image. Keycloak's current non-DHI composition must be evaluated explicitly; its initial review must not rely on future hardening claims.

[ADR-011](../Technical-Documentation/Architecture-Decision-Record/011-buildpacks.md) cited avoiding publicly visible containers as a benefit of the buildpack decision. This proposal revisits that rationale; an approved updated or superseding architecture decision should reconcile it before adoption.

The repository contains seven Dockerfiles. The inventory below describes build outputs and disclosure-review areas; a Dockerfile's presence does not establish that its outputs are deployed or approved for public distribution.

| Image/build definition | What it produces today | Proposed public-read scope and review focus |
|------------------------|------------------------|--------------------------------------------|
| `tdrs-backend/keycloak/Dockerfile` | Keycloak 26.7.3 with nginx/libraries from nginx and UBI stages, config-cli, downloaded jq/curl binaries, all environment realm templates, and startup scripts | First candidate. Inspect `/opt/keycloak/realm-configs/`, scripts, image metadata, and all included upstream layers; verify templates contain placeholders rather than resolved credentials, private keys, or user exports |
| `tdrs-backend/Dockerfile.base` | Python 3.10.8 runtime, Python dependencies (including development dependencies), Graphviz, PostgreSQL client, and a PostgreSQL public signing key | Later hardened base candidate. Inspect dependencies, package-manager configuration/caches, and all distributed layers; distinguish public trust keys from private keys |
| `tdrs-backend/Dockerfile` | Backend base plus the backend context copied into `/tdpapp`; Compose uses it for backend/Celery workloads | Later hardened application candidate. Broad `COPY .` requires review of nested Keycloak/observability assets, fixtures, test data, manifests, and local/generated files, not just Django source |
| `tdrs-frontend/Dockerfile.base` | Node 22 Alpine build/development environment and Yarn dependencies | Later hardened base candidate. Review dependency configuration and any package-registry authentication material |
| `tdrs-frontend/Dockerfile` | Source-bearing `localdev` stage, static frontend build, and final nginx 1.25 Alpine image containing built assets and nginx configuration | Later hardened runtime candidate. Inspect compiled JavaScript, source maps, build-time configuration, and nginx files. Development/build stages and exported build caches are not automatically public-release candidates |
| `tdp-admin/Dockerfile` | Next.js development/build stages and Node 22 Alpine runtime with `.next`, public assets, configuration, and dependencies | Apply the same policy if selected for GHCR deployment. Inspect both server/client build output and dependencies for embedded secrets or sensitive configuration |
| `tdrs-services/parser/Dockerfile` | Go 1.25 build stage and Alpine 3.20 runtime with the compiled parser and `/config` | Apply the same policy if selected for GHCR deployment. Inspect the binary and copied configuration for embedded credentials, endpoints requiring review, and sensitive data |

Compose also pulls third-party database, Redis, LocalStack, ClamAV, observability, exporter, and ZAP images; those references do not authorize making upstream artifacts or local development volumes public. If TDP mirrors or derives another image in a TDP-controlled GHCR package (including security tooling), add it to the inventory and apply the same review before publication.

GHCR visibility is **package-wide**, not a per-tag approval mechanism. Before changing an existing package to public, inventory and inspect every retained version and supported architecture that would become downloadable, including untagged versions and attached artifacts. An unreviewed historical version cannot remain exposed under an approved package. If historical versions cannot be cleared, use a new reviewed package and keep the existing package private. GitHub documents that a public package cannot be made private again. Future pushes to an already-public package are immediately public, so all checks must pass **before** that push.

The operational motivation is to let Cloud.gov pull approved images during deployment and platform-triggered restaging without an expiring personal pull PAT. This does not remove publishing authentication or resolve the separate HHS machine-account request in [#5980](https://github.com/raft-tech/TANF-app/issues/5980). Where a classic PAT remains necessary, comply with the applicable 90-day maximum, assign an owner, and rotate it before expiration. The current Keycloak `deploy.sh` still requires a registry username and `CF_DOCKER_PASSWORD`; anonymous-pull support and restage validation are implementation work after approval.

#### 8.4.2 Repository Review and Built-Image Evidence Status

**Source-review baseline:** commit `26063da5bc73788233c799851ae26c48a54632fe`, reviewed October 26, 2026. The review covered all seven Dockerfiles, their available `.dockerignore` files, Compose build targets, Keycloak realm templates/startup/deployment scripts, the GHCR release workflow, and the repository secret-check scripts. This establishes areas to inspect, not the contents of a released image.

| Area reviewed | Observed result and remaining work |
|---------------|------------------------------------|
| Keycloak credential handling | The six checked-in realm templates use runtime `$(env:...)` substitutions for client secrets and configured Login.gov private keys; their `users` entries define service accounts. `normalize-login-gov-key.sh` reads the key at startup. The Dockerfile copies all six templates. Confirm the exact built contents and review realm/IdP configuration for public suitability, rather than treating field names or placeholder use as proof of absence |
| Build contexts | Backend excludes `.env`/`.env.*` except `.env.example`, but broad copying still includes other nested assets and data types. Frontend explicitly includes `.env.development` and `.env.production`; values can enter compiled output. Admin excludes `.env*`. Parser exclusions cover only build/docs/Markdown/Git and need explicit secret/data review. No Keycloak-context `.dockerignore` is present; its explicit `COPY` list limits copied local files but does not replace inspection |
| Existing secret checks | CircleCI's `secrets-check` job invokes `scripts/git-secrets-check.sh` (recursive source scan using configured patterns) and `scripts/trufflehog-check.sh` (repository scan). The latter sets `--since_commit` to the current branch tip; it does not demonstrate full-tree/history coverage. Neither checks built image layers, image configuration, or generated assets. Validate rules, exclusions, and coverage before relying on these as release gates |
| Existing publishing path | `.github/workflows/publish-release-image.yml` builds/pushes backend and frontend directly, with no explicit sensitive-content or vulnerability gate. Keycloak's Dockerfile documents a manual `buildx --push` command. Neither path establishes the proposed pre-publication checks |
| Built-image inspection | **Pending.** No approved candidate registry reference/digest, all-layer sensitive-content scan report, or final reviewer disposition is recorded here. Local development images or source review cannot substitute for inspection of the exact artifacts proposed for public access |
| Registry/CI settings | Actual GHCR package grants, inherited access, release-ref protections, and CI secret restrictions require settings evidence; workflow YAML alone cannot establish who can publish or replace images |

Before security submission, attach reproducible inspection evidence for each candidate and each retained version that would become public. Use the following record for each platform image, linked to its multi-platform index when applicable:

| Evidence field | Required content |
|----------------|------------------|
| Artifact identity | Full `ghcr.io/<owner>/<package>@sha256:<digest>` reference, associated tags, index/platform digests, architecture, source commit, build job, and base-image digests |
| Inspection method | Tool names/versions, rule/configuration versions, commands, scanner database timestamp where applicable, reviewed paths, and coverage/limitations (including archives, binaries, metadata, and deleted files in earlier layers) |
| Results | Counts and redacted descriptions for credentials/tokens, private keys, sensitive configuration, and sensitive data; separate vulnerability results; manual reviewer and date |
| Disposition | Findings and remediation/false-positive rationale, rebuilt digest and rescan results, and pass/fail/pending status. No unresolved sensitive content is permitted in a public candidate |
| Evidence location | Access-controlled CI artifacts or security-review storage, retention under the existing evidence policy, and a sanitized summary linked from #6176/the documentation PR. Never paste secret values or sensitive records into public issues or reports |

Inspection must cover more than the final merged filesystem:

1. Resolve the exact candidate index and platform digests (for example, `docker buildx imagetools inspect <reference>`). Inspect configuration with `docker image inspect <platform-reference>` and full history with `docker history --no-trunc <platform-reference>` in a restricted review environment; these outputs can themselves reveal secrets.
2. Save the exact platform image with `docker image save <platform-reference> --output image.tar` and use an approved OCI/layer-aware inspection process to examine **every distributed layer**, configuration, and history. A file deleted in a later layer may still be downloadable. A flattened export or a default merged-filesystem scanner alone is insufficient.
3. Run a maintained secret scanner (proposed: Trivy secret scanning with explicit all-layer/metadata coverage, supplemented by manual inspection and additional rules as needed) for tokens/passwords, private keys, credential files, and sensitive configuration/data. Record actual coverage and scan archived/generated content rather than assuming a CVE scanner or filename check detects secrets.
4. Manually review the image-specific areas in the inventory, including Keycloak realm/IdP configuration and service-account definitions, frontend/admin generated output, backend fixtures/data and nested assets, and parser configuration/binary. Classify placeholders, public certificates/trust keys, and synthetic examples explicitly. Review SBOMs, provenance, labels, and any published build caches for disclosure as well.
5. Remediate findings, rebuild, and repeat inspection on the resulting digest. Retain sanitized results and restricted raw evidence; obtain reviewer disposition before proposing a package visibility change. Tool selection and successful execution must be recorded, not inferred from this procedure.

#### 8.4.3 Proposed Controls for Future Builds

These are required target controls for the public publishing path; the source-review findings above identify gaps to close before rollout.

| When | Required check or build practice | Failure handling/evidence |
|------|---------------------------------|---------------------------|
| Pull request / input changes | Scan the full build-context source tree for secrets, keys, sensitive configuration/data; validate repository/history scan coverage. Review Dockerfiles, `.dockerignore`, realm templates, manifests, dependencies, and publishing workflow changes | Block release until findings are removed or documented as non-sensitive false positives; require review of any rule/exclusion changes |
| Build | Use clean, isolated CI contexts and narrow copies. Exclude `.env` files except reviewed public configuration, private keys, credentials, generated deployment manifests, database exports, logs, and real TANF/user data. Inject application/IdP/database secrets only at runtime. If build authentication is necessary, use BuildKit secret mounts; never secret-valued `ARG`/`ENV`, copied credential files, or secrets written into build output/logs | Fail unsafe builds; retain reviewed build configuration. Deleting a secret in a later layer does not remediate the earlier layer |
| Every image/base rebuild, before any public push | Build locally or into a private quarantine location, then scan all distributable layers/configuration/history and review generated output/attached metadata. Run vulnerability scanning separately; apply the approved CVE policy in addition to blocking sensitive content | Fail closed on scan errors, incomplete coverage, or unresolved sensitive findings. Restrict raw reports; record scanner versions, results, commit, and exact inspected artifact identity |
| Promotion/publication | Push the inspected artifact without rebuilding it; verify that the resulting registry digest matches the reviewed content, including each platform manifest and the release index. Attach reviewed SBOM/provenance/signature artifacts through the approved release path | Stop promotion on any digest mismatch or failed check. Do not push an unchecked candidate to an already-public package, even under a temporary tag |
| Base/dependency update and recurring ConMon | Rebuild/rescan on base or dependency updates and review released-image findings, package permissions, publisher credentials/expiry, and unexpected tag/digest changes in the existing monthly/quarterly process | Track remediation under existing vulnerability/incident procedures. Treat newly discovered embedded secrets as exposure; rotate/revoke them and rebuild |

#### 8.4.4 Restricting Who Can Publish or Replace Images

The proposed normal publishing identity is the authorized CI release job, with designated package administrators for visibility/permission management and documented break-glass recovery. Record the actual authorized repositories, teams, machine identities, and owners in restricted configuration/evidence before rollout.

- **Registry grants:** Inventory write/admin access, including repository-inherited permissions and organization owners. Remove unnecessary writers, limit package administration to designated maintainers, and grant Actions access only to approved publishing repositories. Public read access must not broaden write/admin grants. A writer can publish a new version or repoint a tag, so review replacement rights together with initial publication rights.
- **GitHub Actions:** The existing release job uses `contents: read`, `packages: write`, and the job-scoped `GITHUB_TOKEN`; it triggers on version-tag pushes and checks `github.event.base_ref` for `main`/`develop`. Preserve narrow token permissions, but do not treat that conditional as proof of protected release refs, required reviews, or a completed scan. Protect release branches/tags and workflow/Dockerfile changes, verify the release commit is approved, and require successful pre-publication checks. Pull-request/fork jobs must not receive publishing credentials or run untrusted changes with release permissions.
- **CircleCI or other publishers:** If publishing moves to CircleCI, restrict the publishing context to approved projects, identities, and release refs/jobs. A machine-account classic PAT needs `write:packages` and underlying package write permission; avoid unnecessary repository or deletion scopes and authorize organization SSO where required. Keep registry credentials out of build arguments, layers, application runtime variables, and logs. Record ownership, expiration/rotation, and revocation procedures. This is separate from public download access.
- **Administration and recovery:** Separate routine publishing from delete/permission-management operations to the extent supported by package/repository settings. Verify effective permissions, including linked-repository Actions access, rather than assuming token scopes remove package-admin capability. Limit and audit break-glass access; retain the source commit, CI run, reviewed digest, and actor for each release or tag replacement.
- **Deployment integrity:** Pin the approved digest and verify available signatures/provenance through the implemented deployment process. Digest pinning prevents a mutable tag from silently selecting different bytes, but does not replace publisher controls or content inspection.

**Security-review readiness:** Confirm rollout scope and authorized publishers; complete the digest-specific inspection records and remediation; implement/validate the pre-publication gates and permission controls; review the SIA with the requester using the SharePoint copy `ACF SIA _TDP_2026-05-28_V1.0.docx`; and provide the documentation PR, restricted evidence links, and updated SIA location to the requester for security-team submission. Only after approval should designated administrators change visibility and validate anonymous pulls and Cloud.gov restaging. This document update alone does not complete that review package.

### 8.5 Incident Response Detail

The incident response narrative should go beyond rollback and define the expected lifecycle for image-related events.

| Phase | Docker/GHCR-Specific Response |
|-------|-------------------------------|
| **Detection** | Vulnerability/sensitive-content scanner alerts, GHCR package activity, failed GitHub Actions/CircleCI build or deploy checks, image signature/provenance validation failures, CI audit or job anomalies, and available GitHub/GHCR audit events |
| **Triage** | Determine affected image digest, tag, source commit, SBOM components, environments deployed, severity, exploitability, and whether data or credentials may be affected |
| **Containment** | Pause publishing/promotion, revoke compromised publisher access, restrict or remove affected artifacts where supported, rotate/revoke exposed credentials, and redeploy the last known-good digest. Publicly downloaded copies cannot reliably be recalled; deleting an image does not undo disclosure, so assess any sensitive-data exposure through the existing incident process |
| **Eradication** | Rebuild from a patched base image or dependency set, validate scan results, regenerate SBOM/provenance artifacts, and verify configuration against the approved baseline |
| **Recovery** | Promote the remediated image through the normal release path, validate application health, retain evidence, and update vulnerability or POA&M records |

---

## 9. ATO Impact Assessment

### What Changes

#### New Content Required

- **Container image scanning** must be added to the vulnerability management scanning tools table (currently lists OWASP ZAP, Dependabot, and Webinspect — needs a container scanner like Trivy/Grype with defined frequency)
- **Dockerfiles, CircleCI deployment or image-publishing configuration, release image tags, and container image digests** must be added as configuration management artifacts in the CM tools and CM library sections
- **CI/CD pipeline description** must distinguish the current GitHub Actions image publisher from CircleCI deployment and describe the approved target build, pre-publication vulnerability/sensitive-content checks, publishing authentication, GHCR publication, digest verification, and `cf push --docker-image` flow
- **Shared responsibility boundary** must be updated to document TDP team ownership of container runtime environment (base image OS packages, system libraries) vs. cloud.gov ownership of host OS and platform
- **Container image baselines** (Dockerfiles, pinned base image versions) must be added as a distinct baseline type in the configuration baselining section
- **Base image source decision** must reconcile current Dockerfile references to standard public images with the target DHI posture; the approved baseline should identify the selected base image source, owner, patch process, and evidence artifacts
- **Risk summary** may need new entries for container image supply chain risks and their mitigations (DHI, image signing, SLSA provenance)
- **Continuous monitoring procedures** must describe how container findings are reported monthly/quarterly and how unresolved findings feed into vulnerability reporting and POA&M management
- **GHCR registry controls** must describe proposed anonymous public reads, restricted publishing/replacement/admin access, package-wide visibility and historical-version review, authentication, logging limitations, image retention, and incident response expectations
- **Public-release evidence** must identify the exact images/digests and reviewed scope, document sensitive-content inspection results and remediation, and distinguish implemented gates/settings from proposed controls before security approval
- **Incident response procedures** must include detection, triage, containment, eradication, and recovery for compromised, vulnerable, or untrusted container images

#### New Control Narratives Required

- **CM-7 (Least Functionality)** — no standalone section exists in the SSP; needs language about minimizing attack surface via slim/distroless base images
- **SI-7 (Software & Information Integrity)** — no standalone section exists in the SSP; needs language about Docker image signing, digest verification, and SLSA Level 3 provenance
- **SC-28 (Protection of Information at Rest)** — only briefly mentioned; may need a note about container images at rest in a registry

### What Does Not Change

- **Cloud.gov's FedRAMP package** (F1607067912) and all inherited controls remain unchanged.
- **The platform's container runtime**, network security, and isolation guarantees are identical.
- **The application authorization boundary** does not change — applications still run within Cloud.gov's FedRAMP-authorized environment. Public image distribution is nevertheless a changed external artifact-disclosure path that requires security review.

### Recommended Path

This transition should be handled through an **SIA-backed significant change review** with targeted SSP updates rather than assuming a full ATO reassessment is required, since:
- The authorization boundary is unchanged
- Inherited controls are unaffected
- The deployment method is a supported Cloud.gov capability
- The target security posture must be supported by implemented controls and inspection evidence, including assessment of public artifact disclosure
- The SIA can formally document the security relevance, changed implementation responsibilities, and residual risks for AO review

---

## 10. Conclusion

Transitioning from buildpacks to Docker containers built on CIS-validated Hardened Images, or an approved equivalent hardened-image baseline, **maintains our security posture** through Cloud.gov's unchanged inherited controls and **strengthens it** through:

- CIS-benchmarked, continuously scanned base images with near-zero CVEs
- SLSA Level 3 supply chain integrity with cryptographic verification
- Complete SBOMs and audit artifacts that buildpacks cannot provide
- Reduced attack surface through distroless image variants
- Immutable, reproducible deployments that eliminate environment drift

The additional responsibility for base image maintenance is mitigated by DHI's automated patching, continuous scanning, and (if needed) enterprise SLA-backed remediation. Under that target-state model, the TDP team is responsible for monitoring new patches, verifying the patches, and applying them to downstream images rather than managing the full base-image supply chain itself. If the final implementation uses standard public base images instead of DHI or an approved equivalent, the SIA and SSP should document the different residual risk and compensating controls.

Public GHCR readability is a separate proposed access-model change. Its benefit is removing expiring pull-token dependencies; its risk is irreversible disclosure of any sensitive content included in distributed artifacts. Adoption depends on security-team approval of the scope, completed image-inspection evidence, effective publishing restrictions, and validated ongoing checks described in Section 8.4. Hardened base images alone do not establish that TDP-added layers are safe to publish.

---

## References

- [Public-image security review and documentation issue #6176](https://github.com/raft-tech/TANF-app/issues/6176)
- [GHCR identities and Keycloak CI/CD issue #5980](https://github.com/raft-tech/TANF-app/issues/5980)
- [GitHub Container Registry: authentication and anonymous public pulls](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [GitHub Packages: package roles, inheritance, and token scopes](https://docs.github.com/en/packages/learn-github-packages/about-permissions-for-github-packages)
- [GitHub Packages: configuring access control and visibility](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility)
- [Docker build secrets](https://docs.docker.com/build/building/secrets/)
- [Cloud.gov Compliance Overview](https://docs.cloud.gov/platform/compliance/)
- [Cloud.gov ATO Process](https://docs.cloud.gov/platform/compliance/ato-process/)
- [Cloud.gov Docker Deployment](https://docs.cloud.gov/platform/deployment/docker/)
- [Cloud.gov Shared Responsibilities](https://docs.cloud.gov/platform/technology/shared-responsibilities/)
- [Docker Hardened Images Catalog](https://hub.docker.com/hardened-images/catalog)
- [Docker Hardened Images Features](https://docs.docker.com/dhi/features/)
- [Docker Hardened Images — Free for Everyone](https://www.docker.com/blog/docker-hardened-images-for-every-developer/)
- [FedRAMP Compliance with Hardened Images](https://www.docker.com/blog/fedramp-compliance-with-hardened-images/)
- [CIS Docker Benchmark v1.8.0](https://www.cisecurity.org/benchmark/docker)
- [NIST SP 800-190: Application Container Security Guide](https://csrc.nist.gov/publications/detail/sp/800-190/final)
- [Docker Hardened Images — 2026 Architect's Guide](https://mrcloudbook.com/docker-hardened-images-the-2026-architects-guide-to-supply-chain-compliance/)
