#!/bin/sh

set -eu

usage() {
  cat <<'EOF'
Usage:
  scripts/toggle-maintenance-route.sh <enable|disable> <primary-app> <maintenance-app> <domain> [hostname]

Examples:
  # Production custom domain (no hostname)
  scripts/toggle-maintenance-route.sh enable tdp-frontend tdp-frontend-maint tanfdata.acf.hhs.gov
  scripts/toggle-maintenance-route.sh disable tdp-frontend tdp-frontend-maint tanfdata.acf.hhs.gov

  # app.cloud.gov route with hostname
  scripts/toggle-maintenance-route.sh enable tdp-frontend-staging tdp-frontend-staging-maint app.cloud.gov tdp-frontend-staging
  scripts/toggle-maintenance-route.sh disable tdp-frontend-staging tdp-frontend-staging-maint app.cloud.gov tdp-frontend-staging

Notes:
  - You must already be authenticated with Cloud Foundry CLI and target the correct org/space.
  - The maintenance app must already be pushed and healthy.
EOF
}

if [ "$#" -lt 4 ] || [ "$#" -gt 5 ]; then
  usage
  exit 1
fi

ACTION="$1"
PRIMARY_APP="$2"
MAINT_APP="$3"
DOMAIN="$4"
HOSTNAME="${5:-}"

if [ "$ACTION" != "enable" ] && [ "$ACTION" != "disable" ]; then
  echo "Error: action must be 'enable' or 'disable'."
  usage
  exit 1
fi

run_map_route() {
  APP_NAME="$1"
  if [ -n "$HOSTNAME" ]; then
    cf map-route "$APP_NAME" "$DOMAIN" --hostname "$HOSTNAME"
  else
    cf map-route "$APP_NAME" "$DOMAIN"
  fi
}

run_unmap_route() {
  APP_NAME="$1"
  if [ -n "$HOSTNAME" ]; then
    cf unmap-route "$APP_NAME" "$DOMAIN" --hostname "$HOSTNAME"
  else
    cf unmap-route "$APP_NAME" "$DOMAIN"
  fi
}

echo "Verifying target apps exist..."
cf app "$PRIMARY_APP" >/dev/null
cf app "$MAINT_APP" >/dev/null

if [ "$ACTION" = "enable" ]; then
  echo "Enabling maintenance mode: mapping route to maintenance app first."
  run_map_route "$MAINT_APP"

  echo "Removing route from primary app."
  run_unmap_route "$PRIMARY_APP"

  echo "Maintenance mode enabled."
else
  echo "Disabling maintenance mode: mapping route back to primary app first."
  run_map_route "$PRIMARY_APP"

  echo "Removing route from maintenance app."
  run_unmap_route "$MAINT_APP"

  echo "Maintenance mode disabled."
fi

echo "Current route mappings:"
cf app "$PRIMARY_APP"
cf app "$MAINT_APP"
