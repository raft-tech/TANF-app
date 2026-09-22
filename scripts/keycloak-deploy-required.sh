#!/usr/bin/env bash
set -euo pipefail

deploy_required=false

while IFS= read -r path; do
    case "$path" in
        tdrs-backend/keycloak/Dockerfile | \
        tdrs-backend/keycloak/manifest.yml | \
        tdrs-backend/keycloak/deploy.sh | \
        tdrs-backend/keycloak/entrypoint.sh | \
        tdrs-backend/keycloak/nginx.conf | \
        tdrs-backend/keycloak/normalize-login-gov-key.sh | \
        tdrs-backend/keycloak/select-realm-config.sh | \
        tdrs-backend/keycloak/realm-configs/* | \
        .circleci/keycloak/* | \
        .circleci/config.yml | \
        .circleci/base_config.yml | \
        .circleci/generate_config.sh | \
        .circleci/deployment/commands.yml | \
        .circleci/util/commands.yml | \
        .github/workflows/deploy-on-label.yml | \
        scripts/keycloak-deploy-required.sh)
            echo "Keycloak deployment required by: $path"
            deploy_required=true
            ;;
    esac
done

if [ "$deploy_required" == "true" ]; then
    exit 0
fi

echo "No Keycloak build or deployment inputs changed; skipping Keycloak deployment."
exit 1
