#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

cat > "$TEMP_DIR/cf" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

case "$1" in
    app)
        printf '%s\n' "test-app-guid"
        ;;
    push)
        printf '%s\n' "$*" > "$CF_TEST_ARGS"
        printf '%s' "$CF_DOCKER_PASSWORD" > "$CF_TEST_PASSWORD"
        while [ "$#" -gt 0 ]; do
            if [ "$1" = "-f" ]; then
                cp "$2" "$CF_TEST_MANIFEST"
                break
            fi
            shift
        done
        ;;
    target)
        printf '%s\n' "space: tanf-dev"
        ;;
    map-route | add-network-policy)
        ;;
    *)
        echo "Unexpected cf command: $*" >&2
        exit 1
        ;;
esac
EOF
chmod +x "$TEMP_DIR/cf"

CF_TEST_ARGS="$TEMP_DIR/cf-args"
CF_TEST_MANIFEST="$TEMP_DIR/manifest.yml"
CF_TEST_PASSWORD="$TEMP_DIR/cf-password"

CF_TEST_ARGS="$CF_TEST_ARGS" \
CF_TEST_MANIFEST="$CF_TEST_MANIFEST" \
CF_TEST_PASSWORD="$CF_TEST_PASSWORD" \
CF_DOCKER_PASSWORD="test-read-token" \
PATH="$TEMP_DIR:$PATH" \
    bash "$REPO_ROOT/tdrs-backend/keycloak/deploy.sh" \
        -P \
        -e dev \
        -d tdp-keycloak-db-dev \
        -p dev.auth \
        -i ghcr.io/raft-tech/tdp-keycloak@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa \
        -u raft-tdp-ghcr-bot \
        >/dev/null

grep -q -- "--docker-username raft-tdp-ghcr-bot" "$CF_TEST_ARGS"
grep -q -- "ghcr.io/raft-tech/tdp-keycloak@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" "$CF_TEST_ARGS"
grep -q -- 'KC_HOSTNAME: https://dev.auth.tanfdata.acf.hhs.gov' "$CF_TEST_MANIFEST"
grep -q -- 'DEPLOY_ENV: dev' "$CF_TEST_MANIFEST"

if grep -q -- 'CF_DOCKER_PASSWORD\|KEYCLOAK_ADMIN_PASSWORD\|KC_TDP_DJANGO_CLIENT_SECRET' "$CF_TEST_MANIFEST"; then
    echo "Deploy-time or runtime secrets were written to the preserved manifest" >&2
    exit 1
fi

if [ "$(cat "$CF_TEST_PASSWORD")" != "test-read-token" ]; then
    echo "Cloud Foundry did not receive the registry pull token" >&2
    exit 1
fi

if [ -e "$REPO_ROOT/tdrs-backend/keycloak/manifest.tmp.yml" ]; then
    echo "Temporary Keycloak manifest was not removed" >&2
    exit 1
fi

echo "Keycloak preserve-environment deployment test passed."
