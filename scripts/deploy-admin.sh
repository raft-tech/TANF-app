#!/usr/bin/env bash
set -euo pipefail
set +x

if [[ $# != 6 || ! "$1" =~ ^(initial|rolling)$ ]]; then
  echo "Usage: $0 <initial|rolling> <admin-app> <backend-app> <cf-org> <cf-space> <admin-route-domain>" >&2
  exit 1
fi

DEPLOY_STRATEGY=$1
ADMIN_APP_NAME=$2
BACKEND_APP_NAME=$3
CF_ORG=$4
CF_SPACE=$5
ADMIN_ROUTE_DOMAIN=$6
ADMIN_ROUTE_HOSTNAME=${ADMIN_ROUTE_HOSTNAME:-}
ADMIN_ROUTE=$ADMIN_ROUTE_DOMAIN
if [[ -n "$ADMIN_ROUTE_HOSTNAME" ]]; then
  ADMIN_ROUTE="$ADMIN_ROUTE_HOSTNAME.$ADMIN_ROUTE_DOMAIN"
fi

for app_name in "$ADMIN_APP_NAME" "$BACKEND_APP_NAME"; do
  if [[ ! "$app_name" =~ ^[a-zA-Z0-9][a-zA-Z0-9-]*$ ]]; then
    echo "Invalid application name: $app_name" >&2
    exit 1
  fi
done
if [[ "$ADMIN_APP_NAME" == "$BACKEND_APP_NAME" || ! "$ADMIN_ROUTE" =~ ^[a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]{2,}$ ]]; then
  echo "Use distinct app names and a hostname without a scheme, path, or port." >&2
  exit 1
fi
for dependency in cf jq curl; do
  command -v "$dependency" >/dev/null || { echo "Missing dependency: $dependency" >&2; exit 1; }
done

# Verify the existing login instead of silently changing a developer's target.
cf target
TARGET_SPACE_GUID=$(cf space "$CF_SPACE" --guid)
TARGET_ORG_GUID=$(cf org "$CF_ORG" --guid)
BACKEND_GUID=$(cf app "$BACKEND_APP_NAME" --guid)
BACKEND_SPACE_GUID=$(cf curl "/v3/apps/$BACKEND_GUID" | jq -er '.relationships.space.data.guid')
BACKEND_ORG_GUID=$(cf curl "/v3/spaces/$BACKEND_SPACE_GUID" | jq -er '.relationships.organization.data.guid')
if [[ "$BACKEND_SPACE_GUID" != "$TARGET_SPACE_GUID" || "$BACKEND_ORG_GUID" != "$TARGET_ORG_GUID" ]]; then
  echo "The current Cloud.gov target does not match $CF_ORG / $CF_SPACE." >&2
  exit 1
fi

BACKEND_CONFIG=$(cf curl "/v3/apps/$BACKEND_GUID/env")
BACKEND_ENV=$(jq -e '.environment_variables' <<< "$BACKEND_CONFIG")
BACKEND_TOKEN=$(jq -r '.ADMIN_API_PROXY_TOKEN // empty' <<< "$BACKEND_ENV")
BACKEND_ORIGIN=$(jq -r '.ADMIN_FRONTEND_BASE_URL // empty' <<< "$BACKEND_ENV")
BACKEND_COOKIE=$(jq -r '.ADMIN_SESSION_COOKIE_NAME // "admin_sessionid"' <<< "$BACKEND_ENV")
ADMIN_API_PROXY_TOKEN=${ADMIN_API_PROXY_TOKEN:-$BACKEND_TOKEN}
if [[ -z "$ADMIN_API_PROXY_TOKEN" || "$ADMIN_API_PROXY_TOKEN" != "$BACKEND_TOKEN" ]]; then
  echo "Configure a matching ADMIN_API_PROXY_TOKEN on Django before deploying admin." >&2
  exit 1
fi
if [[ "$BACKEND_ORIGIN" != "https://$ADMIN_ROUTE" || "$BACKEND_COOKIE" != "admin_sessionid" ]]; then
  echo "Django must use ADMIN_FRONTEND_BASE_URL=https://$ADMIN_ROUTE and ADMIN_SESSION_COOKIE_NAME=admin_sessionid. Restart Django after configuring them." >&2
  exit 1
fi
# Bound service credentials take precedence over environment variables in Django.
if ! jq -e --arg service "tdp-keycloak-${CF_SPACE#tanf-}" '
  ([.system_env_json.VCAP_SERVICES["user-provided"][]?
    | select(.instance_name == $service) | .credentials][0] // {}) as $credentials
  | (if $credentials | has("tdp_admin_client_secret")
     then $credentials.tdp_admin_client_secret
     else .environment_variables.KEYCLOAK_TDP_ADMIN_CLIENT_SECRET end)
  | type == "string" and length > 0
' <<< "$BACKEND_CONFIG" >/dev/null; then
  echo "Configure Django KEYCLOAK_TDP_ADMIN_CLIENT_SECRET or the bound Keycloak service credential before deploying admin. Restart Django after configuring it." >&2
  exit 1
fi
unset BACKEND_CONFIG BACKEND_ENV BACKEND_TOKEN

if [[ -n "${PREVIOUS_ADMIN_APP_NAME:-}" ]]; then
  if [[ "$PREVIOUS_ADMIN_APP_NAME" == "$ADMIN_APP_NAME" || "$PREVIOUS_ADMIN_APP_NAME" == "$BACKEND_APP_NAME" ]]; then
    echo "The previous admin app must be distinct from the admin and backend apps." >&2
    exit 1
  fi
  cf app "$PREVIOUS_ADMIN_APP_NAME" --guid >/dev/null
fi

# A new route can return 404, but DNS and TLS must work before changing the app.
curl --silent --show-error --output /dev/null --connect-timeout 10 --max-time 15 \
  "https://$ADMIN_ROUTE"

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
DEPLOY_DIR=$(mktemp -d)
trap 'rm -rf "$DEPLOY_DIR"' EXIT
bash "$REPO_ROOT/scripts/prepare-admin-deployment.sh" "$DEPLOY_DIR"

APP_EXISTS=$(cf curl "/v3/apps?space_guids=$TARGET_SPACE_GUID&names=$ADMIN_APP_NAME" |
  jq -r '.resources | if type != "array" then error("Unable to list apps") else length > 0 end')
push_args=(
  "$ADMIN_APP_NAME" -p "$DEPLOY_DIR" -f "$REPO_ROOT/tdp-admin/manifest.yml"
  --var "app-name=$ADMIN_APP_NAME" --var "backend-app-name=$BACKEND_APP_NAME"
  --var "admin-route=$ADMIN_ROUTE"
)

# --no-start stops existing apps; use it only to provision a new app's secret.
if [[ "$APP_EXISTS" == false ]]; then
  cf push "${push_args[@]}" --no-start
fi
cf set-env "$ADMIN_APP_NAME" ADMIN_API_PROXY_TOKEN "$ADMIN_API_PROXY_TOKEN" >/dev/null
unset ADMIN_API_PROXY_TOKEN

cf map-route "$BACKEND_APP_NAME" apps.internal --hostname "$BACKEND_APP_NAME"
cf add-network-policy "$ADMIN_APP_NAME" "$BACKEND_APP_NAME" --protocol tcp --port 8080

if [[ "$APP_EXISTS" == false ]]; then
  cf restart "$ADMIN_APP_NAME"
else
  if [[ "$DEPLOY_STRATEGY" == rolling ]]; then
    push_args+=(--strategy rolling)
  fi
  cf push "${push_args[@]}"
fi

route_args=("$ADMIN_ROUTE_DOMAIN")
if [[ -n "$ADMIN_ROUTE_HOSTNAME" ]]; then
  route_args+=(--hostname "$ADMIN_ROUTE_HOSTNAME")
fi
# Auth and callbacks must share the admin origin for host-only Django cookies.
cf map-route "$BACKEND_APP_NAME" "${route_args[@]}" --path admin-auth
cf map-route "$ADMIN_APP_NAME" "${route_args[@]}"
if [[ -n "${PREVIOUS_ADMIN_APP_NAME:-}" ]]; then
  cf unmap-route "$PREVIOUS_ADMIN_APP_NAME" "${route_args[@]}"
fi

curl --fail --silent --show-error --retry 5 --retry-delay 2 --retry-connrefused \
  --connect-timeout 10 --max-time 30 "https://$ADMIN_ROUTE/api/health" | jq -e '.ok == true'
curl --fail --silent --show-error --connect-timeout 10 --max-time 30 \
  "https://$ADMIN_ROUTE/api/backend-health" | jq -e '.ok == true'
curl --fail --silent --show-error --connect-timeout 10 --max-time 30 \
  "https://$ADMIN_ROUTE/admin-auth/auth_check" | jq -e '.authenticated == false'
cf app "$ADMIN_APP_NAME"
