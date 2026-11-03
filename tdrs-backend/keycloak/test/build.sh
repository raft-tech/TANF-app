#!/usr/bin/env bash
set -euo pipefail
: "${IMAGE_REF:?Supply a local image tag}"
: "${PLATFORM:?Supply an explicit platform}"
cd "$(git rev-parse --show-toplevel)"
results="tdrs-backend/keycloak/test/results/build-$(date -u +%Y%m%dT%H%M%SZ)-$$"
mkdir -p "$results"
exec > >(tee "$results/build.log") 2>&1
echo "Source commit: $(git rev-parse HEAD)"
echo "Requested image: $IMAGE_REF; platform: $PLATFORM"
echo 'Production source diff (must be reviewed if nonempty):'
git diff HEAD -- tdrs-backend/keycloak ':!tdrs-backend/keycloak/test'
BUILDX_METADATA_PROVENANCE=max docker buildx build --load --platform "$PLATFORM" \
    --metadata-file "$results/metadata.json" --tag "$IMAGE_REF" tdrs-backend/keycloak
docker image inspect "$IMAGE_REF" --format 'ID={{.Id}} Platform={{.Os}}/{{.Architecture}} Digests={{json .RepoDigests}}'
image_id="$(docker image inspect "$IMAGE_REF" --format '{{.Id}}')"
container="kc-baseline-versions-$(date +%s)-$$"
cleanup() {
    docker rm -f "$container" >/dev/null 2>&1 || true
}
trap cleanup EXIT
docker run --pull=never --name "$container" --network none --platform "$PLATFORM" --entrypoint /bin/bash "$image_id" -c '
  set -e
  /opt/keycloak/bin/kc.sh --version
  java -version
  nginx -v
  jq --version
  curl --version
'
docker cp "$container:/opt/keycloak/keycloak-config-cli.jar" "$results/config-cli.jar"
python3 - "$results/config-cli.jar" <<'PY'
import sys
import zipfile

with zipfile.ZipFile(sys.argv[1]) as jar:
    print("Config-cli artifact manifest:\n" + jar.read("META-INF/MANIFEST.MF").decode())
PY
echo "Build evidence: $results (local only; retain the image ID for comparison)"
