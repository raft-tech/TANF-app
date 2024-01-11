#!/bin/bash

##############################
# Global Variable Decls 
##############################

CF_SPACE=${1}
ENV=${2}

DEPLOY_STRATEGY=${3-tbd}
CELERY_DEPLOY_STRATEGY=${4-tbd}

CGAPPNAME_FRONTEND="tdp-frontend-${ENV}"
CGAPPNAME_BACKEND="tdp-backend-${ENV}"
CGAPPNAME_CELERY="tdp-celery-${ENV}"

strip() {
  # Usage: strip "string" "pattern"
  printf '%s\n' "${1##$2}"
}
# The cloud.gov space defined via CF_SPACE environment variable (e.g., "tanf-dev", "tanf-staging")
space=$(strip $CF_SPACE "tanf-")

echo DEPLOY_STRATEGY: "$DEPLOY_STRATEGY"
echo BACKEND_HOST: "$CGAPPNAME_BACKEND"
echo CELERY_HOST: "$CGAPPNAME_CELERY"
echo CF_SPACE: "$CF_SPACE"
echo space: "$space"
echo environment: "$ENV"


##############################
# Function Decls
##############################

set_cf_envs() {
  var_list=(
    "ACFTITAN_HOST"
    "ACFTITAN_KEY"
    "ACFTITAN_USERNAME"
    "AMS_CLIENT_ID"
    "AMS_CLIENT_SECRET"
    "AMS_CONFIGURATION_ENDPOINT"
    "BASE_URL"
    "CLAMAV_NEEDED"
    "CYPRESS_TOKEN"
    "DJANGO_CONFIGURATION"
    "DJANGO_DEBUG"
    "DJANGO_SECRET_KEY"
    "DJANGO_SETTINGS_MODULE"
    "DJANGO_SU_NAME"
    "FRONTEND_BASE_URL"
    "LOGGING_LEVEL"
    "JWT_KEY"
    "STAGING_JWT_KEY"
  )

  echo "Setting environment variables for $1"

  for var_name in ${var_list[@]}; do
    # Intentionally unsetting variable if empty
    if [[ -z "${!var_name}" ]]; then
      echo "WARNING: Empty value for $var_name. It will now be unset."
      cf_cmd="cf unset-env $1 $var_name ${!var_name}"
      $cf_cmd
      continue
    elif [[ ($var_name =~ 'STAGING_') && ($CF_SPACE = 'tanf-staging') ]]; then
      sed_var_name=$(echo "$var_name" | sed -e 's@STAGING_@@g')
      cf_cmd="cf set-env $1 $sed_var_name ${!var_name}"
    else
      cf_cmd="cf set-env $1 $var_name ${!var_name}"
    fi
    
    echo "Setting var : $var_name"
    $cf_cmd
  done

}

# Helper method to generate JWT cert and keys for new environment
generate_jwt_cert() {
  echo "regenerating JWT cert/key"
  yes 'XX' | openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -sha256
  cf set-env "$CGAPPNAME_BACKEND" JWT_CERT "$(cat cert.pem)"
  cf set-env "$CGAPPNAME_BACKEND" JWT_KEY "$(cat key.pem)"
}

update_backend() {
  cd tdrs-backend || exit
  cf unset-env "$CGAPPNAME_BACKEND" "AV_SCAN_URL"
  cf unset-env "$CGAPPNAME_BACKEND" "CGAPPNAME_BACKEND"
  cf unset-env "$CGAPPNAME_CELERY" "CGAPPNAME_BACKEND"
  # Let Celery know backend app name for s3 file searching 
  cf set-env "$CGAPPNAME_BACKEND" CGAPPNAME_BACKEND "$CGAPPNAME_BACKEND"
  cf set-env "$CGAPPNAME_CELERY" CGAPPNAME_BACKEND "$CGAPPNAME_BACKEND"
  
  if [[ $CF_SPACE == 'tanf-prod' ]]; then
    cf set-env "$CGAPPNAME_BACKEND" AV_SCAN_URL "http://tanf-prod-clamav-rest.apps.internal:9000/scan"
  else
    # Add environment varilables for clamav
    cf set-env "$CGAPPNAME_BACKEND" AV_SCAN_URL "http://tdp-clamav-nginx-$space.apps.internal:9000/scan"
  fi

  if [[ $1 == 'rolling' ]] ; then
    set_cf_envs $CGAPPNAME_BACKEND
    # Do a zero downtime deploy.  This requires enough memory for
    # two apps to exist in the org/space at one time.
    cf push "$CGAPPNAME_BACKEND" --no-route -f manifest.buildpack.yml -t 180 --strategy rolling || exit 1
  else
    cf push "$CGAPPNAME_BACKEND" --no-route -f manifest.buildpack.yml -t 180
    # set up JWT key if needed
    if cf e "$CGAPPNAME_BACKEND" | grep -q JWT_KEY ; then
      echo jwt cert already created
    else
      generate_jwt_cert
    fi
  fi

  if [[ $2 == 'rolling' ]] ; then
    set_cf_envs $CGAPPNAME_CELERY
    # Do a zero downtime deploy.  This requires enough memory for
    # two apps to exist in the org/space at one time.
    cf push "$CGAPPNAME_CELERY" --no-route -f manifest.celery.yml -t 180 --strategy rolling || exit 1
  else
    cf push "$CGAPPNAME_CELERY" --no-route -f manifest.celery.yml -t 180
  fi

  if [[ ! "$CF_SPACE" == "tanf-prod" ]]; then
    #allow dev envs to monitor celery through flower/prometheus
    cf map-route "$CGAPPNAME_CELERY" app.cloud.gov --hostname "${CGAPPNAME_CELERY}"
  fi

  set_cf_envs $CGAPPNAME_BACKEND
  set_cf_envs $CGAPPNAME_CELERY
  # Let Celery know backend app name for s3 file searching 
  cf set-env "$CGAPPNAME_BACKEND" CGAPPNAME_BACKEND "$CGAPPNAME_BACKEND"
  cf set-env "$CGAPPNAME_CELERY" CGAPPNAME_BACKEND "$CGAPPNAME_BACKEND"
  
  cf map-route "$CGAPPNAME_BACKEND" apps.internal --hostname "$CGAPPNAME_BACKEND"

  # Add network policy to allow frontend to access backend
  cf add-network-policy "$CGAPPNAME_FRONTEND" "$CGAPPNAME_BACKEND" --protocol tcp --port 8080
  
  if [[ $CF_SPACE == 'tanf-prod' ]]; then
    # Add network policy to allow backend to access tanf-prod services
    cf add-network-policy "$CGAPPNAME_BACKEND" clamav-rest --protocol tcp --port 9000
  else
    cf add-network-policy "$CGAPPNAME_BACKEND" tdp-clamav-nginx-$space --protocol tcp --port 9000
  fi

}

bind_backend_to_services() {
  echo "Binding services to app: $CGAPPNAME_BACKEND"

  if [[ $CGAPPNAME_BACKEND = 'tdp-backend-develop' ]]; then
    # TODO: this is technical debt, we should either make staging mimic tanf-dev 
    #       or make unique services for all apps but we have a services limit
    #       Introducing technical debt for release 3.0.0 specifically.
    space="develop"
  fi

  cf bind-service "$CGAPPNAME_BACKEND" "tdp-staticfiles-${space}"
  cf bind-service "$CGAPPNAME_BACKEND" "tdp-datafiles-${space}"
  cf bind-service "$CGAPPNAME_BACKEND" "tdp-db-${space}"

  cf bind-service "$CGAPPNAME_CELERY" "tdp-staticfiles-${space}"
  cf bind-service "$CGAPPNAME_CELERY" "tdp-datafiles-${space}"
  cf bind-service "$CGAPPNAME_CELERY" "tdp-db-${space}"

  # bind to redis
  cf bind-service "$CGAPPNAME_BACKEND" "tdp-redis-${ENV}"
  cf bind-service "$CGAPPNAME_CELERY" "tdp-redis-${ENV}"  
  # bind to elastic-search
  cf bind-service "$CGAPPNAME_BACKEND" "es-${ENV}"
  cf bind-service "$CGAPPNAME_CELERY" "es-${ENV}"
  
  set_cf_envs $CGAPPNAME_BACKEND
  set_cf_envs $CGAPPNAME_CELERY

  echo "Restarting apps: $CGAPPNAME_BACKEND and $CGAPPNAME_CELERY"
  cf restage "$CGAPPNAME_BACKEND"
  cf restage "$CGAPPNAME_CELERY"
}

##############################
# Main script body
##############################

# Determine the appropriate BASE_URL for the deployed instance based on the
# provided Cloud.gov App Name
DEFAULT_ROUTE="https://$CGAPPNAME_FRONTEND.app.cloud.gov"
if [[ -n $BASE_URL ]]; then
  # Use Shell Parameter Expansion to replace localhost in the URL
  BASE_URL="${BASE_URL//http:\/\/localhost:8080/$DEFAULT_ROUTE}"
elif [[ $CF_SPACE == 'tanf-prod' ]]; then
  # Keep the base url set explicitly for production.
  BASE_URL="https://tanfdata.acf.hhs.gov/v1"
elif [[ $CF_SPACE == 'tanf-staging' ]]; then
  # use .acf.hss.gov domain for develop and staging.
  BASE_URL="https://$CGAPPNAME_FRONTEND.acf.hhs.gov/v1"
else
  # Default to the route formed with the cloud.gov env for the lower environments.
  BASE_URL="$DEFAULT_ROUTE/v1"
fi

DEFAULT_FRONTEND_ROUTE="${DEFAULT_ROUTE//backend/frontend}"
if [[ -n $FRONTEND_BASE_URL ]]; then
  FRONTEND_BASE_URL="${FRONTEND_BASE_URL//http:\/\/localhost:3000/$DEFAULT_FRONTEND_ROUTE}"
elif [[ $CF_SPACE == 'tanf-prod' ]]; then
  # Keep the base url set explicitly for production.
  FRONTEND_BASE_URL='https://tanfdata.acf.hhs.gov'
elif [[ $CF_SPACE == 'tanf-staging' ]]; then
   # use .acf.hss.gov domain for develop and staging.
  FRONTEND_BASE_URL="https://$CGAPPNAME_FRONTEND.acf.hhs.gov"
else
  # Default to the route formed with the cloud.gov env for the lower environments.
  FRONTEND_BASE_URL="$DEFAULT_FRONTEND_ROUTE"
fi

# Dynamically generate a new DJANGO_SECRET_KEY
DJANGO_SECRET_KEY=$(python3 -c "from secrets import token_urlsafe; print(token_urlsafe(50))")

# Dynamically set DJANGO_CONFIGURATION based on Cloud.gov Space
DJANGO_SETTINGS_MODULE="tdpservice.settings.cloudgov"
if [[ $CF_SPACE == 'tanf-prod' ]]; then
  DJANGO_CONFIGURATION="Production"
elif [[ $CF_SPACE == 'tanf-staging' ]]; then
  DJANGO_CONFIGURATION="Staging"
else
  DJANGO_CONFIGURATION="Development"
  DJANGO_DEBUG="Yes"
  CYPRESS_TOKEN=$CYPRESS_TOKEN
fi

APP_GUID=$(cf app $CGAPPNAME_BACKEND --guid || true)
CELERY_GUID=$(cf app $CGAPPNAME_CELERY --guid || true)

if [[ $DEPLOY_STRATEGY == 'tbd' ]]; then
  if [[ $APP_GUID == 'FAILED' ]]; then
    DEPLOY_STRATEGY='initial'
  else
    DEPLOY_STRATEGY='rolling'
  fi
  echo "Setting backend deployment strategy: ${DEPLOY_STRATEGY}"
else
  echo "Using given backend deployment strategy: ${DEPLOY_STRATEGY}"
fi

if [[ $CELERY_DEPLOY_STRATEGY == 'tbd' ]]; then
  if [[ $CELERY_GUID == 'FAILED' ]]; then
    CELERY_DEPLOY_STRATEGY='initial'
  else
    CELERY_DEPLOY_STRATEGY='rolling'
  fi
  echo "Setting celery deployment strategy: ${CELERY_DEPLOY_STRATEGY}"
else
  echo "Using given celery deployment strategy: ${CELERY_DEPLOY_STRATEGY}"
fi

if [[ $DEPLOY_STRATEGY == 'rebuild' ]]; then
  # You want to redeploy the instance under the same name
  # Delete the existing app (with out deleting the services)
  # and perform the initial deployment strategy.
  cf delete "$CGAPPNAME_BACKEND" -r -f
  cf delete "$CGAPPNAME_CELERY" -r -f
fi

if [[ $DEPLOY_STRATEGY == 'bind' ]]; then
  # Bind the services the application depends on and restage the app.
  bind_backend_to_services
else
  update_backend $DEPLOY_STRATEGY $CELERY_DEPLOY_STRATEGY
fi

if [[ $DEPLOY_STRATEGY == 'initial' ]]; then
  bind_backend_to_services
elif [[ $DEPLOY_STRATEGY == 'rebuild' ]]; then
  bind_backend_to_services
elif [[ $CELERY_DEPLOY_STRATEGY == 'initial' ]]; then
  bind_backend_to_services
elif [[ $CELERY_DEPLOY_STRATEGY == 'rebuild' ]]; then
  bind_backend_to_services
else
  echo "no need to rebind to services"
fi
