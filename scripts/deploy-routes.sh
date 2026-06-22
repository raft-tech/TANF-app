#!/bin/sh

TDP_FRONTEND_DOMAIN="tanfdata.acf.hhs.gov"
TDP_KEYCLOAK_PUBLIC_DOMAIN="auth.tanfdata.acf.hhs.gov"
TDP_INTERNAL_DOMAIN="apps.internal"

frontend_public_host() {
  case "$1" in
    tdp-frontend-raft)
      echo "test.${TDP_FRONTEND_DOMAIN}"
      ;;
    tdp-frontend-qasp)
      echo "qasp.${TDP_FRONTEND_DOMAIN}"
      ;;
    tdp-frontend-a11y)
      echo "a11y.${TDP_FRONTEND_DOMAIN}"
      ;;
    tdp-frontend-develop)
      echo "develop.${TDP_FRONTEND_DOMAIN}"
      ;;
    tdp-frontend-staging)
      echo "staging.${TDP_FRONTEND_DOMAIN}"
      ;;
    tdp-frontend-prod)
      echo "${TDP_FRONTEND_DOMAIN}"
      ;;
    *)
      return 1
      ;;
  esac
}

keycloak_public_host_for_env() {
  case "$1" in
    dev)
      echo "dev.${TDP_KEYCLOAK_PUBLIC_DOMAIN}"
      ;;
    staging)
      echo "staging.${TDP_KEYCLOAK_PUBLIC_DOMAIN}"
      ;;
    prod)
      echo "${TDP_KEYCLOAK_PUBLIC_DOMAIN}"
      ;;
    *)
      return 1
      ;;
  esac
}

keycloak_internal_host_for_env() {
  case "$1" in
    dev)
      echo "dev-auth.${TDP_INTERNAL_DOMAIN}"
      ;;
    staging)
      echo "staging-auth.${TDP_INTERNAL_DOMAIN}"
      ;;
    prod)
      echo "auth.${TDP_INTERNAL_DOMAIN}"
      ;;
    *)
      return 1
      ;;
  esac
}

keycloak_public_url_for_space() {
  case "$1" in
    tanf-prod)
      echo "https://$(keycloak_public_host_for_env prod)"
      ;;
    tanf-staging)
      echo "https://$(keycloak_public_host_for_env staging)"
      ;;
    *)
      echo "https://$(keycloak_public_host_for_env dev)"
      ;;
  esac
}

keycloak_internal_url_for_space() {
  case "$1" in
    tanf-prod)
      echo "http://$(keycloak_internal_host_for_env prod):8080"
      ;;
    tanf-staging)
      echo "http://$(keycloak_internal_host_for_env staging):8080"
      ;;
    *)
      echo "http://$(keycloak_internal_host_for_env dev):8080"
      ;;
  esac
}

keycloak_tdp_redirect_uris_for_env() {
  case "$1" in
    dev)
      echo "https://test.${TDP_FRONTEND_DOMAIN}/*,https://qasp.${TDP_FRONTEND_DOMAIN}/*,https://a11y.${TDP_FRONTEND_DOMAIN}/*"
      ;;
    staging)
      echo "https://develop.${TDP_FRONTEND_DOMAIN}/*,https://staging.${TDP_FRONTEND_DOMAIN}/*"
      ;;
    prod)
      echo "https://${TDP_FRONTEND_DOMAIN}/*"
      ;;
    *)
      return 1
      ;;
  esac
}

keycloak_tdp_web_origins_for_env() {
  case "$1" in
    dev)
      echo "https://test.${TDP_FRONTEND_DOMAIN},https://qasp.${TDP_FRONTEND_DOMAIN},https://a11y.${TDP_FRONTEND_DOMAIN}"
      ;;
    staging)
      echo "https://develop.${TDP_FRONTEND_DOMAIN},https://staging.${TDP_FRONTEND_DOMAIN}"
      ;;
    prod)
      echo "https://${TDP_FRONTEND_DOMAIN}"
      ;;
    *)
      return 1
      ;;
  esac
}

route_domain_for_fqdn() {
  case "$1" in
    "${TDP_KEYCLOAK_PUBLIC_DOMAIN}")
      echo "${TDP_KEYCLOAK_PUBLIC_DOMAIN}"
      ;;
    *".${TDP_KEYCLOAK_PUBLIC_DOMAIN}")
      echo "${TDP_KEYCLOAK_PUBLIC_DOMAIN}"
      ;;
    "${TDP_FRONTEND_DOMAIN}")
      echo "${TDP_FRONTEND_DOMAIN}"
      ;;
    *".${TDP_FRONTEND_DOMAIN}")
      echo "${TDP_FRONTEND_DOMAIN}"
      ;;
    "${TDP_INTERNAL_DOMAIN}")
      echo "${TDP_INTERNAL_DOMAIN}"
      ;;
    *".${TDP_INTERNAL_DOMAIN}")
      echo "${TDP_INTERNAL_DOMAIN}"
      ;;
    *)
      return 1
      ;;
  esac
}

route_hostname_for_fqdn() {
  route_fqdn="$1"
  route_domain="$(route_domain_for_fqdn "$route_fqdn")" || return 1

  if [ "$route_fqdn" = "$route_domain" ]; then
    return 0
  fi

  echo "${route_fqdn%.$route_domain}"
}

cf_domain_exists() {
  cf domains 2>/dev/null | awk '{print $1}' | grep -Fx "$1" >/dev/null 2>&1
}

map_route_for_fqdn() {
  route_app="$1"
  route_fqdn="$2"

  if cf_domain_exists "$route_fqdn"; then
    route_domain="$route_fqdn"
    route_hostname=""
  else
    if ! route_domain="$(route_domain_for_fqdn "$route_fqdn")"; then
      echo "Unsupported route domain for FQDN: $route_fqdn"
      return 1
    fi
    if ! route_hostname="$(route_hostname_for_fqdn "$route_fqdn")"; then
      echo "Unsupported route hostname for FQDN: $route_fqdn"
      return 1
    fi
  fi

  if [ -n "$route_hostname" ]; then
    cf map-route "$route_app" "$route_domain" --hostname "$route_hostname"
  else
    cf map-route "$route_app" "$route_domain"
  fi
}
