#!/bin/bash
set -e

DEV_BACKEND_APPS=("tdp-backend-test" "tdp-backend-qasp" "tdp-backend-a11y")
DEV_CELERY_APPS=("tdp-celery-test" "tdp-celery-qasp" "tdp-celery-a11y")
STAGING_BACKEND_APPS=("tdp-backend-develop" "tdp-backend-staging")
STAGING_CELERY_APPS=("tdp-celery-develop" "tdp-celery-staging")
PROD_BACKEND="tdp-backend-prod"
PROD_CELERY="tdp-celery-prod"

PUBLIC_DOMAIN="tanfdata.acf.hhs.gov"

# Environment variables needed to bootstrap or explicitly reconfigure an app.
# CI preserves the existing runtime environment and does not need these values.
RUNTIME_ENV_VARS=(
    "KEYCLOAK_ADMIN"              # Admin console username
    "KEYCLOAK_ADMIN_PASSWORD"     # Admin console password
    "KC_TDP_DJANGO_CLIENT_SECRET" # tdp-django client secret (realm config)
    "KC_TDP_ADMIN_CLIENT_SECRET"  # tdp-admin client secret (admin realm config)
    "LOGIN_GOV_JWT_KEY"           # Login.gov RSA private key (PEM or base64)
    "AMS_CLIENT_ID"                # AMS OIDC client ID
    "AMS_CLIENT_SECRET"            # AMS OIDC client secret
)
OPTIONAL_ENV_VARS=(
    "KEYCLOAK_REALM"               # Standard TDP realm name
    "KEYCLOAK_TDP_ADMIN_REALM"     # Admin TDP realm name
    "KEYCLOAK_CONFIG_IMPORT_ON_STARTUP" # Run config-cli from entrypoint after Keycloak readiness
    "LOGIN_GOV_ACR_VALUES"         # Login.gov identity assurance level
    "LOGIN_GOV_CLIENT_ID"           # Login.gov OIDC client ID
    "LOGIN_GOV_AUTH_URL"            # Login.gov authorization endpoint
    "LOGIN_GOV_TOKEN_URL"           # Login.gov token endpoint
    "LOGIN_GOV_JWKS_URL"            # Login.gov JWKS endpoint
    "LOGIN_GOV_LOGOUT_URL"          # Login.gov logout endpoint
    "LOGIN_GOV_ISSUER"              # Login.gov issuer
    "AMS_AUTH_URL"                  # AMS authorization endpoint
    "AMS_TOKEN_URL"                 # AMS token endpoint
    "AMS_JWKS_URL"                  # AMS JWKS endpoint
    "AMS_LOGOUT_URL"                # AMS logout endpoint
    "AMS_USERINFO_URL"              # AMS userinfo endpoint
    "AMS_ISSUER"                    # AMS issuer
    "KC_CLI_REDIRECT_URI"           # Additional redirect URI for tdp-cli
    "KC_CLI_WEB_ORIGIN"             # Additional web origin for tdp-cli
    "KC_TDP_GRAFANA_CLIENT_SECRET"  # tdp-grafana client secret (realm config)
)

help() {
    echo "Deploy Keycloak to the Cloud Foundry space you're currently authenticated in."
    echo ""
    echo "Syntax: deploy.sh [-hP] -e <environment> -d <rds_service_name> -p <public_hostname> -i <docker_image> -u <docker_username>"
    echo ""
    echo "Options:"
    echo "  h     Print this help message."
    echo "  e     Target environment: dev, staging, or prod."
    echo "        For dev/staging, the CF app name and internal route hostname are suffixed"
    echo "        (e.g. keycloak-dev, keycloak-staging). For prod, no suffix is added (keycloak)."
    echo "  r     Use rolling deployment strategy. Default is a standard (stop-start) deploy."
    echo "        WARNING: do NOT use -r when upgrading the Keycloak version — the rolling"
    echo "        strategy runs old and new instances simultaneously, which can cause DB"
    echo "        migration conflicts and authentication failures during the transition."
    echo "  P     Preserve the existing Cloud Foundry runtime environment. This is intended"
    echo "        for CI redeployments of an existing app and fails if the app does not exist."
    echo "  d     The Cloud Foundry service name of the RDS instance (e.g. tdp-db-dev)."
    echo "  p     The public hostname for Keycloak (e.g. dev.auth)."
    echo "        This will create a public route at <hostname>.${PUBLIC_DOMAIN}"
    echo "        and set KC_HOSTNAME so Keycloak generates correct redirect URIs."
    echo "  i     An immutable Keycloak image URI (e.g. ghcr.io/hhs/tdp-keycloak@sha256:<digest>)."
    echo "  u     Docker registry username. Password must be set via CF_DOCKER_PASSWORD env var."
    echo ""
    echo "Required environment variables (must be set in your shell):"
    for var in "${RUNTIME_ENV_VARS[@]}"; do
        echo "  $var"
    done
    echo "  CF_DOCKER_PASSWORD"
    echo ""
    echo "Optional environment variables:"
    for var in "${OPTIONAL_ENV_VARS[@]}"; do
        echo "  $var"
    done
    echo ""
    echo "Example:"
    echo "  ./deploy.sh -e dev -d tdp-keycloak-db-dev -p dev.auth -i ghcr.io/raft-tech/tdp-keycloak@sha256:<digest> -u <ghcr-robot>"
    echo ""
}

check_required_env_vars() {
    local missing=()
    for var in "$@"; do
        if [ -z "${!var:-}" ]; then
            missing+=("$var")
        fi
    done
    if [ ${#missing[@]} -gt 0 ]; then
        echo "Error: the following required environment variables are not set:"
        for var in "${missing[@]}"; do
            echo "  $var"
        done
        echo ""
        echo "Set them in your shell before running this script."
        popd
        exit 1
    fi
}

inject_env_vars() {
    local manifest="$1"

    for var in "${RUNTIME_ENV_VARS[@]}" "${OPTIONAL_ENV_VARS[@]}"; do
        if [ -n "${!var:-}" ]; then
            # Use yq strenv() to safely handle values with special characters
            export "${var?}"
            yq eval -i ".applications[0].env.$var = strenv($var)" "$manifest"
        fi
    done
}

set_manifest_env() {
    local manifest="$1"
    local var="$2"
    local value="$3"

    export "$var=$value"
    yq eval -i ".applications[0].env.$var = strenv($var)" "$manifest"
}

inject_default_config_cli_env_vars() {
    local manifest="$1"
    local default_login_gov_client_id

    set_manifest_env "$manifest" "KEYCLOAK_CONFIG_IMPORT_ON_STARTUP" "${KEYCLOAK_CONFIG_IMPORT_ON_STARTUP:-true}"

    case "$DEPLOY_ENV" in
        dev)
            default_login_gov_client_id="urn:gov:gsa:openidconnect.profiles:sp:sso:hhs:tanf-proto-dev"
            ;;
        staging)
            default_login_gov_client_id="urn:gov:gsa:openidconnect.profiles:sp:sso:hhs:tanf-proto-staging"
            ;;
        prod)
            default_login_gov_client_id="urn:gov:gsa:openidconnect.profiles:sp:sso:hhs:tanf-prod"
            ;;
    esac

    set_manifest_env "$manifest" "LOGIN_GOV_CLIENT_ID" "${LOGIN_GOV_CLIENT_ID:-$default_login_gov_client_id}"
    set_manifest_env "$manifest" "LOGIN_GOV_AUTH_URL" "${LOGIN_GOV_AUTH_URL:-https://idp.int.identitysandbox.gov/openid_connect/authorize}"
    set_manifest_env "$manifest" "LOGIN_GOV_TOKEN_URL" "${LOGIN_GOV_TOKEN_URL:-https://idp.int.identitysandbox.gov/api/openid_connect/token}"
    set_manifest_env "$manifest" "LOGIN_GOV_JWKS_URL" "${LOGIN_GOV_JWKS_URL:-https://idp.int.identitysandbox.gov/api/openid_connect/certs}"
    set_manifest_env "$manifest" "LOGIN_GOV_LOGOUT_URL" "${LOGIN_GOV_LOGOUT_URL:-https://idp.int.identitysandbox.gov/openid_connect/logout}"
    set_manifest_env "$manifest" "LOGIN_GOV_ISSUER" "${LOGIN_GOV_ISSUER:-https://idp.int.identitysandbox.gov/}"
    set_manifest_env "$manifest" "LOGIN_GOV_ACR_VALUES" "${LOGIN_GOV_ACR_VALUES:-http://idmanagement.gov/ns/assurance/ial/1}"

    set_manifest_env "$manifest" "KC_TDP_GRAFANA_CLIENT_SECRET" "${KC_TDP_GRAFANA_CLIENT_SECRET:-}"

    set_manifest_env "$manifest" "AMS_AUTH_URL" "${AMS_AUTH_URL:-https://sso-stage.acf.hhs.gov/auth/realms/ACF-SSO/protocol/openid-connect/auth}"
    set_manifest_env "$manifest" "AMS_TOKEN_URL" "${AMS_TOKEN_URL:-https://sso-stage.acf.hhs.gov/auth/realms/ACF-SSO/protocol/openid-connect/token}"
    set_manifest_env "$manifest" "AMS_JWKS_URL" "${AMS_JWKS_URL:-https://sso-stage.acf.hhs.gov/auth/realms/ACF-SSO/protocol/openid-connect/certs}"
    set_manifest_env "$manifest" "AMS_LOGOUT_URL" "${AMS_LOGOUT_URL:-https://sso-stage.acf.hhs.gov/auth/realms/ACF-SSO/protocol/openid-connect/logout}"
    set_manifest_env "$manifest" "AMS_USERINFO_URL" "${AMS_USERINFO_URL:-https://sso-stage.acf.hhs.gov/auth/realms/ACF-SSO/protocol/openid-connect/userinfo}"
    set_manifest_env "$manifest" "AMS_ISSUER" "${AMS_ISSUER:-https://sso-stage.acf.hhs.gov/auth/realms/ACF-SSO}"

    set_manifest_env "$manifest" "KC_CLI_REDIRECT_URI" "${KC_CLI_REDIRECT_URI:-http://localhost/*}"
    set_manifest_env "$manifest" "KC_CLI_WEB_ORIGIN" "${KC_CLI_WEB_ORIGIN:-http://localhost}"
}

deploy_keycloak() {
    local app_name="$1"
    local db_service="$2"
    local public_hostname="$3"
    local docker_image="$4"
    local docker_username="$5"
    local rolling="$6"
    local preserve_runtime_env="$7"
    local public_url="https://${public_hostname}.${PUBLIC_DOMAIN}"

    MANIFEST=manifest.tmp.yml
    cp manifest.yml $MANIFEST

    yq eval -i ".applications[0].name = \"${app_name}\"" "$MANIFEST"
    yq eval -i ".applications[0].services[0] = \"${db_service}\"" "$MANIFEST"
    yq eval -i ".applications[0].env.KC_HOSTNAME = \"${public_url}\"" "$MANIFEST"
    yq eval -i ".applications[0].env.DEPLOY_ENV = \"${DEPLOY_ENV}\"" "$MANIFEST"
    yq eval -i ".applications[0].docker.image = \"${docker_image}\"" "$MANIFEST"
    if [ "$preserve_runtime_env" != "true" ]; then
        inject_env_vars "$MANIFEST"
        inject_default_config_cli_env_vars "$MANIFEST"
    fi

    local strategy_args=()
    if [ "$rolling" == "true" ]; then
        strategy_args=(--strategy rolling)
    fi

    CF_DOCKER_PASSWORD="$CF_DOCKER_PASSWORD" cf push --no-route -f "$MANIFEST" "${strategy_args[@]}" --docker-image "$docker_image" --docker-username "$docker_username"

    # Internal route for server-to-server communication (backend/celery -> keycloak)
    cf map-route "$app_name" apps.internal --hostname "$app_name"

    # Public route for browser redirects and admin console access
    cf map-route "$app_name" "$public_hostname"."$PUBLIC_DOMAIN"

    rm "$MANIFEST"
}

setup_keycloak_net_pols() {
    local app_name="$1"
    CURRENT_SPACE=$(cf target | grep -Eo "tanf-[a-z]+")

    if [ "$CURRENT_SPACE" == "tanf-dev" ]; then
        for app in "${DEV_BACKEND_APPS[@]}" "${DEV_CELERY_APPS[@]}"; do
            cf add-network-policy "$app" "$app_name" --protocol tcp --port 8080
        done
    elif [ "$CURRENT_SPACE" == "tanf-staging" ]; then
        for app in "${STAGING_BACKEND_APPS[@]}" "${STAGING_CELERY_APPS[@]}"; do
            cf add-network-policy "$app" "$app_name" --protocol tcp --port 8080
        done
    elif [ "$CURRENT_SPACE" == "tanf-prod" ]; then
        cf add-network-policy $PROD_BACKEND "$app_name" --protocol tcp --port 8080
        cf add-network-policy $PROD_CELERY "$app_name" --protocol tcp --port 8080
    fi
}

pushd "$(dirname "$0")"
trap 'rm -f "${MANIFEST:-}"' EXIT

ROLLING="false"
PRESERVE_RUNTIME_ENV="false"

while getopts ":he:rPd:p:i:u:" option; do
   case $option in
      h) # display Help
         help
         exit;;
      e) # Target environment
         DEPLOY_ENV=$OPTARG;;
       r) # Rolling strategy
          ROLLING="true";;
       P) # Preserve existing runtime environment
          PRESERVE_RUNTIME_ENV="true";;
      d) # RDS service name
         DB_SERVICE_NAME=$OPTARG;;
      p) # Public hostname
         PUBLIC_HOSTNAME=$OPTARG;;
      i) # Docker image
         DOCKER_IMAGE=$OPTARG;;
      u) # Docker username
         DOCKER_USERNAME=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         echo
         help
         popd
         exit 1;;
   esac
done

if [ "$#" -eq 0 ]; then
    help
    exit
fi

if [ "$DEPLOY_ENV" == "" ]; then
    echo "Error: you must specify an environment with -e (dev, staging, or prod)."
    echo
    help
    popd
    exit 1
fi

case "$DEPLOY_ENV" in
    dev)
        APP_NAME="keycloak-dev"
        ;;
    staging)
        APP_NAME="keycloak-staging"
        ;;
    prod)
        APP_NAME="keycloak"
        ;;
    *)
        echo "Error: invalid environment '${DEPLOY_ENV}'. Must be dev, staging, or prod."
        echo
        help
        popd
        exit 1
        ;;
esac

if [ "$DB_SERVICE_NAME" == "" ]; then
    echo "Error: you must include a database service name with -d."
    echo
    help
    popd
    exit 1
fi

if [ "$PUBLIC_HOSTNAME" == "" ]; then
    echo "Error: you must include a public hostname with -p."
    echo
    help
    popd
    exit 1
fi

if [ "$DOCKER_IMAGE" == "" ]; then
    echo "Error: you must include a Docker image with -i."
    echo
    help
    popd
    exit 1
fi

if [ "$DOCKER_USERNAME" == "" ]; then
    echo "Error: you must include a Docker username with -u."
    echo
    help
    popd
    exit 1
fi

if [ -z "${CF_DOCKER_PASSWORD:-}" ]; then
    check_required_env_vars "CF_DOCKER_PASSWORD"
fi

if [ "$PRESERVE_RUNTIME_ENV" == "true" ]; then
    if ! cf app "$APP_NAME" --guid >/dev/null 2>&1; then
        echo "Error: -P can only redeploy an existing Cloud Foundry app (${APP_NAME})."
        popd
        exit 1
    fi
else
    check_required_env_vars "${RUNTIME_ENV_VARS[@]}"
fi

echo "Deploying Keycloak..."
echo "  Environment:    $DEPLOY_ENV"
echo "  App name:       $APP_NAME"
echo "  Docker image:   $DOCKER_IMAGE"
echo "  RDS service:    $DB_SERVICE_NAME"
echo "  Internal route: ${APP_NAME}.apps.internal"
echo "  Public route:   ${PUBLIC_HOSTNAME}.${PUBLIC_DOMAIN}"
echo "  Rolling deploy: $ROLLING"
echo "  Preserve env:   $PRESERVE_RUNTIME_ENV"
echo ""

deploy_keycloak "$APP_NAME" "$DB_SERVICE_NAME" "$PUBLIC_HOSTNAME" "$DOCKER_IMAGE" "$DOCKER_USERNAME" "$ROLLING" "$PRESERVE_RUNTIME_ENV"
setup_keycloak_net_pols "$APP_NAME"

popd
