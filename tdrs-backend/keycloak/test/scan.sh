#!/usr/bin/env bash
set -euo pipefail
: "${IMAGE_REF:?Supply an existing local image}"
: "${PLATFORM:?Supply an explicit platform}"
cd "$(git rev-parse --show-toplevel)"
scanner=aquasec/trivy:0.76.1@sha256:790fd66d1697395d8693d1acaa1ea702406a20f109b6fc7bac8db623eca6c06c
results="tdrs-backend/keycloak/test/results/scan-$(date -u +%Y%m%dT%H%M%SZ)-$$"
cache=tdrs-backend/keycloak/test/results/trivy-cache
mkdir -p "$results" "$cache"
exec > >(tee "$results/scan.log") 2>&1
image_id="$(docker image inspect "$IMAGE_REF" --format '{{.Id}}')"
actual_platform="$(docker image inspect "$image_id" --format '{{.Os}}/{{.Architecture}}')"
[[ "$actual_platform" == "$PLATFORM" ]] || { echo "Platform mismatch: $actual_platform != $PLATFORM" >&2; exit 1; }
printf 'UTC: %s\nImage: %s\nID: %s\nPlatform: %s\nScanner: %s\n' \
    "$(date -u +%FT%TZ)" "$IMAGE_REF" "$image_id" "$PLATFORM" "$scanner"
docker image inspect "$image_id" > "$results/image.json"
# An archive avoids granting the scanner access to the Docker daemon/socket.
docker image save "$image_id" --output "$results/image.tar"
scan() {
    docker run --rm --mount "type=bind,src=$PWD/$results,dst=/evidence" \
        --mount "type=bind,src=$PWD/$cache,dst=/cache" "$scanner" "$@"
}
scan --version
scan image --cache-dir /cache --input /evidence/image.tar \
    --scanners vuln --ignorefile /dev/null --list-all-pkgs --format json --output /evidence/scan.json
scan image --cache-dir /cache --input /evidence/image.tar \
    --format cyclonedx --output /evidence/sbom.cdx.json
scan --cache-dir /cache --version
cp "$cache/db/metadata.json" "$results/vulnerability-db.json"
cp "$cache/java-db/metadata.json" "$results/java-db.json"
# Evaluate the full unsuppressed report; no ignore file, VEX, or unfixed filter.
python3 - "$results/scan.json" <<'PY'
import collections
import json
import sys

with open(sys.argv[1]) as source:
    report = json.load(source)
results = report.get("Results", [])
if not any(result.get("Class") == "os-pkgs" for result in results):
    sys.exit("BLOCKED: OS package analysis is missing")
if not any(result.get("Type") == "jar" for result in results):
    sys.exit("BLOCKED: Java dependency analysis is missing")
counts = collections.Counter(
    finding["Severity"]
    for result in results
    for finding in result.get("Vulnerabilities", [])
)
print("Findings:", dict(counts))
if counts["CRITICAL"] or counts["HIGH"]:
    sys.exit("BLOCKED: Critical/High findings require remediation; see retained scan.json")
PY
