#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
FILTER="$SCRIPT_DIR/keycloak-deploy-required.sh"

assert_deploy() {
    if ! printf '%s\n' "$1" | "$FILTER" >/dev/null; then
        echo "Expected Keycloak deployment for $1" >&2
        exit 1
    fi
}

assert_skip() {
    if printf '%s\n' "$1" | "$FILTER" >/dev/null; then
        echo "Expected Keycloak deployment to skip for $1" >&2
        exit 1
    fi
}

assert_deploy "tdrs-backend/keycloak/Dockerfile"
assert_deploy "tdrs-backend/keycloak/realm-configs/realm-export.prod.json"
assert_deploy ".circleci/keycloak/jobs.yml"
assert_deploy ".circleci/config.yml"
assert_deploy ".circleci/deployment/commands.yml"
assert_deploy "scripts/keycloak-deploy-required.sh"
assert_skip "tdrs-backend/keycloak/README.md"
assert_skip "tdrs-backend/tdpservice/users/oidc.py"
assert_skip "tdrs-frontend/src/App.js"

echo "Keycloak deployment path filter tests passed."
