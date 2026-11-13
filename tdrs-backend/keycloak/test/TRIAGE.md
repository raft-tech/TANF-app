# Phase 2 vulnerability triage — 2026-11-03

## Security remediation follow-up

The subsequently authorized Keycloak 26.8.1 / config-cli security rebuild removed
all original Java Critical/High reports and curl's findings. The first ARM64 raw
scan (`results/scan-20261103T185610Z-43268`) has **0 Critical / 3 High**:

| Advisory | Package | Installed DHI version | Remaining assessment |
| --- | --- | --- | --- |
| CVE-2026-54369 | libacl1 | 2.3.2-2+deb13u0+dhi2 | Path-based ACL functions remain present; non-root operation constrains exploitation, but does not establish a package fix. |
| CVE-2026-16742 | libsystemd0 | 257.13-1~deb13u1+dhi2 | Advisory concerns systemd-homed, not the shared library; both final candidates lack that executable. |
| CVE-2025-69720 | libtinfo6 | 6.5+20250216-2+deb13u0+dhi5 | Advisory concerns infocmp, not the shared library; both final candidates lack that executable. |

Official DHI VEX at advisory repository revision
`78e7781a8e6e5018945299dc4442c50ec17a73f7`,
`vex/keycloak/dhi-keycloak.vex.json`, marks all three `not_affected` with the
justification `vulnerable_code_cannot_be_controlled_by_adversary`. However, the
notes only cite Debian `no-dsa` status. Debian's ACL tracker explicitly marks
trixie vulnerable, with 2.4.0-1 fixed in unstable and a future stable point update
planned. **No-dsa is not evidence of a fix.** No VEX or ignore filtering has been
enabled, and these reports remain blocking under the approved raw-scan gate.

The VEX signature was verified successfully (`Verified OK`) with the adjacent
Sigstore bundle and the public key fetched over HTTPS from
`https://registry.scout.docker.com/keyring/dhi/latest`, using DHI Cosign 3 pinned
to `sha256:71d12564b8c5af3ad0e56312cdfd5fda5f8fd6b62b5e703c15275ff6cd5df179`.
The exact JSON, bundle, and key are retained in `results/triage-20261103/`.
Authenticity is established; application-specific applicability is not thereby
proven. A vendor-fixed compatible DHI base or an explicitly approved, narrowly
scoped applicability policy is needed before this security gate can pass.
Do not mix unstable Debian libraries into the hardened runtime or remove package
metadata merely to satisfy the scanner.

Both final architecture scans reproduce the same three High findings; exact IDs
and evidence paths are recorded in [README.md](README.md). Offline filesystem
inspection of both final immutable images confirms UID/GID 65532 and no
systemd-homed, systemd-homework, infocmp, or setuid/setgid files under `/usr` and
`/opt`. This is static applicability evidence, not a deployed-runtime guarantee
or an approved scanner exception.

## Historical triage outcome and boundaries (before remediation)

Static triage of all **42 blocking observations / 22 distinct advisories** found:

- **1 High version-identification false positive with strong artifact evidence:** SQL Server JDBC.
- **2 High observations whose affected executable is absent:** systemd-homed and ncurses infocmp.
- **11 High plus 1 Critical observations with important prerequisite/usage constraints:** curl, ACL, PCRE2, OpenSSL, FreeMarker, Spring Boot, and Spring Expression.
- **27 High observations requiring further call-path/dependency assessment:** Jackson (26 observations across server/admin CLI/config-cli) and Guava (1).

These categories account for the original **1 Critical / 41 High** findings; they
are triage conclusions, **not an adjusted scan result, signed VEX, suppression,
exception, or release approval**. The existing unsuppressed security gate remains
failed. No remote exploitability was demonstrated. No server, authentication,
import, persistence, or failure smoke tests were run.

The user committed the Phase 2 implementation at `0bf8b7d39` before this triage;
the worktree was clean when triage began. This does not establish security
acceptance. No Dockerfile, source, realm, scanner policy, release reference,
publication, deployment, or existing service/database was changed during triage.

## Evidence scope

Original reports (Trivy 0.76.1, OS DB updated 2026-11-03 13:13:42 UTC / Java DB
01:08:45 UTC):

- AMD64: `results/scan-20261103T182048Z-33927/scan.json`, image
  `sha256:24ad74e12ac7ad83716b3cb0dafa10f029f59bf6adcec3154773a18d45274dd5`.
- ARM64: `results/scan-20261103T181959Z-33522/scan.json`, image
  `sha256:97d75a3b6b40f8d395cf775b0a4d8ade114c47585e8fe17715bc9beefd632369`.

Both reports have the same blocking advisories/counts. Read-only filesystem
checks ran on **both immutable candidates**, offline and without service mounts;
they confirmed UID/GID 65532, no effective capabilities in the inspection process,
no setuid/setgid files under `/usr` or `/opt`, and no systemd-homed, systemd-homework,
infocmp, setfacl, or getfacl executables. This describes the inspected containers,
not a verified Cloud.gov runtime security configuration.

Local ignored evidence is in `results/triage-20261103/`: copied candidate JARs,
per-advisory GitHub API snapshots, `platform-checks.log`, and
`freemarker-bytecode.log`. Docker-backed research used ephemeral Task YAML on
stdin; JAR inspection used the already-pinned DHI dev image's `javap` with
network disabled and a read-only artifact mount. No exploit payloads were run.
GitHub global advisory records were retrieved for 21 advisories; systemd's global
query returned no record, so its repository advisory was reviewed instead. No
retrieved global advisory record was marked withdrawn. Trivy's `Status: fixed`
means a fix is available in the advisory's package ecosystem, not that the
installed candidate package has that fix.

## Per-advisory triage

Counts are package/JAR observations, not independent exploits. **Every row still
requires remediation or formally reviewed evidence disposition before acceptance.**

| Advisory | Scan severity / count | Triage and evidence | Recommended next action |
| --- | --- | --- | --- |
| CVE-2026-84939 | Critical / 1 | Vulnerable FreeMarker 2.3.32 is genuinely present, but the inspected default theme loader and classpath utility do not accept a request-selected locale; all six checked-in realms also disable internationalization. | Prefer an upstream-remediated server base; security may review constrained reachability, but this is not yet a complete not-affected determination. |
| CVE-2026-12064 | High / 2 | Requires schemeless SFTP/SCP plus `--proto-default`; the supported curl call is fixed `http://127.0.0.1:9000/health/ready` with neither option, and curl upstream rates this Low. | Review not-triggered-by-supported-usage evidence and DHI backports; prefer a patched curl package when available rather than changing severity locally. |
| CVE-2026-8458 | High / 2 | Requires Negotiate-authenticated connection reuse across different services; startup polling uses no authentication and separate curl processes, and curl upstream rates this Low. | Same package/backport and security applicability review as the preceding curl finding. |
| CVE-2026-54369 | High / 1 | ACL library is present, but the reported escalation requires a privileged pathname-based ACL caller; the runtime is non-root and no setfacl/getfacl or setuid/setgid executable was found in the inspected locations. | Ask DHI for patch/VEX evidence or use an updated base; do not call non-root alone proof that the library is unaffected. |
| CVE-2026-103111 | High / 1 | PCRE2 is genuinely behind the reported fixed package revision, but exploitation needs attacker-controlled regex compilation plus particular JIT API usage; checked-in nginx uses prefix locations with no `pcre_jit on`, and startup grep patterns are fixed and do not use `-P`. | Update via a compatible newer DHI base; retain conditional rather than demonstrated remote exposure. |
| CVE-2026-84782 | High / 3 | Affected OpenSSL package revisions are present, but this advisory concerns DTLS, not ordinary TLS; nginx is an HTTP proxy with no DTLS configuration and readiness curl uses local HTTP. | Prefer updated DHI OpenSSL packages/base; document no identified DTLS path without generalizing that all OpenSSL use is safe. |
| CVE-2026-16742 | High / 1 | Strong affected-code-absent evidence: advisory targets systemd-homed/homework, neither binary exists in either candidate, and `libsystemd0` presence does not install that service. | Submit this exact-image evidence for a not-affected/package-scope disposition, not a blanket systemd suppression. |
| CVE-2025-69720 | High / 1 | Strong affected-code-absent evidence: flaw is in ncurses `progs/infocmp.c`; the candidates contain libtinfo but no infocmp executable. | Submit this exact-image evidence for a not-affected/package-scope disposition; vendor severities differ, so do not silently re-rate it. |
| CVE-2026-68494 | High / 2 | Both observations are inside config-cli; the bypass needs non-blocking/chunked numeric parsing, which is not demonstrated by its trusted-file startup import path. | Update/rebuild config-cli dependencies or obtain a complete parser-path applicability review. |
| CVE-2026-89407 | High / 4 | Two observations are config-cli and two are the server/admin CLI; attacker-controlled string-to-number coercion can trigger the regex issue, and server JSON processing remains potentially reachable pending a concrete endpoint/type trace. | Prioritize a server base with fixed Jackson and a separate compatible config-cli dependency update. |
| CVE-2026-89425 | High / 4 | Requires Jackson's `DataInput` parser; the inspected Keycloak JSON utility exposes byte-array, String, and InputStream reads, not DataInput, but this does not exhaustively cover all server/framework/import paths. | Update Jackson through upstream distributions; investigate DataInput callers before any not-affected claim. |
| CVE-2026-54512 | High / 2 | Both observations are config-cli and require polymorphic deserialization plus a validator configuration; its application classes contain no direct default-typing activation reference, but dependencies/models were not exhaustively proven free of that configuration. | Treat as conditional, not confirmed code execution; update config-cli or complete the mapper/model call-path review. |
| CVE-2026-54513 | High / 2 | Both observations are config-cli and require the array-subtype allow-list configuration; no direct application default-typing activation was found, which is not proof that every dependency mapper is safe. | Same compatible config-cli update or complete mapper/model review as CVE-2026-54512. |
| CVE-2026-68497 | High / 2 | Both observations are config-cli and require binding to XML Duration/XMLGregorianCalendar types; no direct references to those target types were found in its application classes, but dependency model paths remain unproven. | Update config-cli or finish the target-type/call-path applicability analysis. |
| CVE-2026-91776 | High / 4 | Two observations are config-cli and two are the server/admin CLI; requires name-based polymorphism with fallback and a reused mapper, not just accepting arbitrary JSON. | Update server/config-cli Jackson; investigate annotated models and fallback configuration before declaring exposure or absence. |
| CVE-2026-91777 | High / 4 | Two observations are config-cli and two are the server/admin CLI; requires identity-enabled collections/maps and forward references, and no direct JsonIdentityInfo reference was found in config-cli's application classes. | Update server/config-cli Jackson; dependency/model and framework paths remain open. |
| CVE-2026-102554 | High / 1 | Guava 33.5.0-jre is present, but the advisory requires crafted native Java object deserialization, not normal JSON/OIDC traffic; no exposed collection-deserialization path has been demonstrated. | Use an upstream server distribution with Guava 33.7.2 or later and review deserialization consumers if seeking an applicability disposition. |
| CVE-2025-59250 | High / 1 | Strong version-mapping false positive: the exact candidate driver bytes match Maven Central's fixed 13.2.1.jre11 artifact, while its embedded pom.properties says 13.2.1, explaining the scanner's missing suffix; additionally the image is augmented for PostgreSQL. | Correct/report the identification with hash/advisory evidence; do not remove an internal server JAR as a shortcut. |
| CVE-2026-40973 | High / 1 | Config-cli's actual embedded configuration sets `spring.main.web-application-type=NONE`; the advisory's servlet persistent-session/temp-directory scenario is not the supported startup CLI model. | Strong as-configured non-applicability candidate for security review; retain the finding until disposition and avoid broad Spring Boot exceptions. |
| CVE-2026-41850 | High / 1 | Requires attacker-supplied SpEL evaluation; config-cli exposes no web listener and consumes operator-controlled configuration, and its application classes have no direct SpelExpressionParser reference. | Review trusted-input/indirect Spring evaluation boundaries or update Spring as part of a compatible config-cli rebuild. |
| CVE-2026-29062 | High / 1 | Config-cli's Jackson 3.0.1 includes affected nesting-limit parser paths, but there is no demonstrated untrusted nested-document path in the supported startup-only imports. | Upgrade config-cli's Jackson 3 dependency set or complete parser/input-boundary review. |
| GHSA-2m67-wjpj-xhg9 | High / 1 | Config-cli's Jackson 3.0.1 can bypass document-length constraints; trusted checked-in import files reduce exposure but do not repair the library or prove all server-response parsing safe. | Upgrade the compatible Jackson 3 dependency set; do not rely on a size guard this advisory says can be bypassed. |

## Important evidence details

### SQL Server driver: not merely a filename guess

Actual candidate artifact:

`/opt/keycloak/lib/lib/main/com.microsoft.sqlserver.mssql-jdbc-13.2.1.jre11.jar`

- SHA256: `2d137aa308c78932878952fe3624ea090ecfe644414b8b23e71a305f425698c5`.
- Matches the published [Maven Central artifact checksum](https://repo.maven.apache.org/maven2/com/microsoft/sqlserver/mssql-jdbc/13.2.1.jre11/mssql-jdbc-13.2.1.jre11.jar.sha256).
- Embedded Maven `version=13.2.1` omits the `jre11` suffix.
- [GHSA-m494-w24q-6f7w](https://github.com/advisories/GHSA-m494-w24q-6f7w)
  explicitly lists 13.2.1.jre11 as fixed and the affected range ends **before** it.

### FreeMarker: vulnerable component versus request reachability

The actual copied services JAR was disassembled, not inferred only from a source
tag. `DefaultFreeMarkerProvider.getTemplate` creates a Configuration with a theme
loader and calls `getTemplate(templateName, "UTF-8")`; it does not set a
request-supplied locale. `FreemarkerUtils.loadTemplateFromClasspath` similarly
uses a classpath loader and no request locale argument. Those are the only
classes referencing FreeMarker Configuration in the inspected services JAR.
The realm locale selector also returns English immediately when internationalization
is disabled, as in all six checked-in realm exports. That is corroborating
context, **not the same setting as FreeMarker's own localized lookup**, which
has not been explicitly disabled here.

The advisory requires an attacker-controlled malformed locale reaching template
lookup. That prerequisite has not been demonstrated in these paths. Other JARs,
custom/future providers/themes, template-side settings, deployed realm differences,
and actual runtime overrides were not exhaustively assessed. The vulnerable
2.3.32 component remains present; do not label this globally unaffected or lower
its scanner severity without formal review.

Sources:
[advisory](https://github.com/advisories/GHSA-27j2-h3m2-8237),
[default provider](https://github.com/keycloak/keycloak/blob/26.7.3/services/src/main/java/org/keycloak/theme/freemarker/DefaultFreeMarkerProvider.java),
[classpath utility](https://github.com/keycloak/keycloak/blob/26.7.3/services/src/main/java/org/keycloak/utils/FreemarkerUtils.java),
[locale selector](https://github.com/keycloak/keycloak/blob/26.7.3/services/src/main/java/org/keycloak/locale/DefaultLocaleSelectorProvider.java).

### Config-cli is a separate, startup-only process

The exact approved release JAR SHA256 remains
`df6939a1d9c40d5ab7e1fb690082ea8980dbbf402ca92a9968b90b652cb3ca9a`.
Its embedded application.properties confirms `web-application-type=NONE` and
Keycloak target 26.5.5. The repository runs it as a separate JVM against loopback
after Keycloak readiness and before nginx. It imports checked-in files with
operator-provided substitutions; it also parses Keycloak Admin API responses,
so "not an HTTP server" does **not** prove all its JSON input trusted.

Application-class constant searches found no direct references to
activateDefaultTyping, enableDefaultTyping, JsonTypeInfo, JsonIdentityInfo,
SpelExpressionParser, StandardEvaluationContext, XMLGregorianCalendar, or
javax.xml.datatype.Duration. These are limited negative indicators, not a
complete reflection/dependency/annotation call graph or proof of non-exploitability.

The GitHub latest-release API still reports **v6.5.1**. The **20 High observations
inside config-cli** therefore need a separate compatible patched artifact/source
build or formally reviewed applicability determinations; updating only Keycloak
cannot fix them.

Sources:
[release](https://github.com/adorsys/keycloak-config-cli/releases/tag/v6.5.1),
[application configuration](https://github.com/adorsys/keycloak-config-cli/blob/v6.5.1/src/main/resources/application.properties),
[Keycloak JSON utility](https://github.com/keycloak/keycloak/blob/26.7.3/core/src/main/java/org/keycloak/util/JsonSerialization.java).

### OS findings: no silent severity or vendor-patch assumptions

[curl's CVE-2026-12064 advisory](https://curl.se/docs/CVE-2026-12064.json) and
[CVE-2026-8458 advisory](https://curl.se/docs/CVE-2026-8458.json) rate both Low;
the retained Trivy report uses other vendors' severity values and reports High.
Record the discrepancy rather than choosing the lower value to pass the gate.
Upstream lists 8.14.2 as a fixed maintenance release, but no suitable verified DHI
curl package update has been selected or approved here. Backports must be checked
against exact DHI package patch/VEX evidence, not inferred from version suffixes.

The [systemd advisory](https://github.com/systemd/systemd/security/advisories/GHSA-jm29-p7hh-vjhv)
specifically concerns homed's home-record handling, not generic libsystemd APIs.
The [ncurses advisory](https://github.com/advisories/GHSA-9952-mrqj-h4jh)
identifies infocmp code, not the libtinfo library alone.
[PCRE2](https://github.com/PCRE2Project/pcre2/security/advisories/GHSA-r9hj-j2rw-4q3m)
and [OpenSSL](https://openssl-library.org/news/secadv/20260929.txt) require their
specific regex/JIT and DTLS prerequisites. No Docker Scout plugin was installed,
so no signed DHI VEX was retrieved/verified; this report is not a substitute.

## Verified remediation candidate, not an authorized upgrade

Registry research confirmed `dhi.io/keycloak:26-debian13` currently resolves to
26.8.1. The explicit 26.8.1 index is:

`sha256:cf5c35691dc4e48a9cbade9d707a8df0cb35f9cfd5a25735ed9d447b0576e017`

That image was downloaded and inspected **offline on ARM64 only**, without
starting Keycloak or modifying the selected candidate. Its actual main-library
filenames/package metadata contain:

| Component | Current candidate | Inspected 26.8.1 base | Interpretation |
| --- | --- | --- | --- |
| FreeMarker | 2.3.32 | 2.3.35 | Matches the advisory fixed version. |
| Jackson Core | 2.21.4 | 2.21.7 | Matches the reported fixes for the server main-library findings. |
| Jackson Databind | 2.22.2 | 2.22.3 | Matches the reported fixes for the server main-library findings. |
| Guava | 33.5.0-jre | 33.7.2-jre | Matches the advisory fixed version. |
| SQL Server JDBC | 13.2.1.jre11 | 13.4.0.jre11 | Newer than the reported fixed release. |
| PCRE2 | 10.46-1~deb13u2+dhi0 | 10.46-1~deb13u3+dhi0 | Meets the scanner's reported fixed package revision. |
| OpenSSL family | 3.5.7-1~deb13u2+dhi1 | 3.5.7-1~deb13u3+dhi0 | Meets the scanner's reported fixed package revision. |
| Java | 21.0.12+8 | 21.0.13+9 | Remains Java 21. |

This is **not a clean scan of a new derived image**, confirmation of every shaded
admin-CLI dependency, AMD64 execution verification, config-cli compatibility
validation, database-upgrade approval, or runtime acceptance. The newer base may
have other findings. New assembly-stage pins would also need verification.

## Recommended order and decision gate

1. **Security review of evidence corrections:** exact fixed SQL Server artifact,
   absent homed, and absent infocmp; maintainers/security should approve any
   per-artifact VEX or scanner-correction mechanism before changing the gate.
2. **Request explicit server-upgrade approval:** evaluate DHI Keycloak 26.8.1
   rather than replacing internal server JARs; consider database migration,
   backup/recovery and config-cli compatibility before using it with any database.
3. **Separately choose config-cli remediation:** approve a pinned upstream source
   build with a compatible patched Spring/Jackson set, or obtain an upstream
   fixed release and review the conditional findings; do not swap nested JARs ad hoc.
4. **Check remaining DHI OS patches/VEX and curl fixes:** retain exact package
   provenance and the existing zero-Critical/High policy until formally changed.
5. **Only after those decisions:** rebuild both architectures, repeat offline
   checks/backend regression/lint and full unsuppressed scans; stop again for
   manual review without publishing/deploying or restoring automated smoke tests.

TDP Keycloak image maintainers own coordination with DHI/config-cli maintainers;
the team's security reviewer owns applicability/exception approval. No named
reviewer, waiver, or remediation implementation was supplied/created by this triage.
