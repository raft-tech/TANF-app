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
docker image inspect "$image_id" > "$results/image.json"
actual_platform="$(docker image inspect "$image_id" --format '{{.Os}}/{{.Architecture}}')"
[[ "$actual_platform" == "$PLATFORM" ]] || { echo "Platform mismatch: $actual_platform != $PLATFORM" >&2; exit 1; }
container="kc-baseline-versions-$(date +%s)-$$"
cleanup() {
    docker rm -f "$container" >/dev/null 2>&1 || true
}
trap cleanup EXIT
docker run --pull=never --name "$container" --network none --platform "$PLATFORM" --entrypoint /bin/bash "$image_id" -c '
  set -eu
  id
  /opt/keycloak/bin/kc.sh --version
  java -version
  nginx -v
  jq --version
  curl --version
  if [ -d /usr/share/keycloak-image ]; then
    test "$(id -u)" -ne 0
    test -w /opt/keycloak/data/import
    test -w /tmp/nginx_proxy
    for utility in bash sh java sed grep find xargs curl jq base64 dirname cp mkdir; do
      command -v "$utility"
    done
    for utility in apt-get dpkg gcc javac; do
      if command -v "$utility"; then
        echo "Unexpected build/package tool in final runtime: $utility" >&2
        exit 1
      fi
    done
    sha256sum -c /usr/share/keycloak-image/copied-files.sha256
    printf "%s  %s\n" df6939a1d9c40d5ab7e1fb690082ea8980dbbf402ca92a9968b90b652cb3ca9a /opt/keycloak/keycloak-config-cli.jar | sha256sum -c -
    sed "s/LISTEN_PORT/8080/" /opt/keycloak/nginx.conf.template > /tmp/nginx.conf
    nginx -t -c /tmp/nginx.conf
    printf "{\"architectureCheck\":true}\n" | jq -e .architectureCheck
    printf "utility-check\n" | grep -q utility-check
  fi
'
docker cp "$container:/opt/keycloak/keycloak-config-cli.jar" "$results/config-cli.jar"
python3 - "$results/config-cli.jar" <<'PY'
import sys
import zipfile

with zipfile.ZipFile(sys.argv[1]) as jar:
    print("Config-cli artifact manifest:\n" + jar.read("META-INF/MANIFEST.MF").decode())
PY
echo "Build evidence: $results (local only; retain the image ID for comparison)"
