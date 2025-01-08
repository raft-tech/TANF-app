#!/bin/bash

##############################
# Global Variable Decls
##############################

# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

#The application name  defined via the manifest yml for the frontend
CGAPPNAME_FRONTEND=${2}
CGAPPNAME_BACKEND=${3}
CGAPPNAME_KIBANA=${4}
CGAPPNAME_PROXY=${5}
CF_SPACE=${6}

strip() {
    # Usage: strip "string" "pattern"
    printf '%s\n' "${1##$2}"
}
# The cloud.gov space defined via environment variable (e.g., "tanf-dev", "tanf-staging")
env=$(strip $CF_SPACE "tanf-")
backend_app_name=$(echo $CGAPPNAME_BACKEND | cut -d"-" -f3)
tf_path="terraform/$env"

# Update the Kibana and Elastic proxy names to include the environment
CGAPPNAME_KIBANA="${CGAPPNAME_KIBANA}-${env}"
CGAPPNAME_PROXY="${CGAPPNAME_PROXY}-${env}"

echo DEPLOY_STRATEGY: "$DEPLOY_STRATEGY"
echo BACKEND_HOST: "$CGAPPNAME_BACKEND"
echo KIBANA_HOST: "$CGAPPNAME_KIBANA"
echo ELASTIC_PROXY_HOST: "$CGAPPNAME_PROXY"
echo CF_SPACE: "$CF_SPACE"
echo env: "$env"
echo backend_app_name: "$backend_app_name"
echo terraform path: "$tf_path"

##############################
# Function Decls
##############################

# Helper method to generate JWT cert and keys for new environment
generate_jwt_cert()
{
    echo "regenerating JWT cert/key"
    yes 'XX' | openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -sha256
    #cf set-env "$CGAPPNAME_BACKEND" JWT_CERT "$(cat cert.pem)"
    #cf set-env "$CGAPPNAME_BACKEND" JWT_KEY "$(cat key.pem)"
    #TODO: to ENV then create_backend_vars.sh should transpose it.
}

prepare_promtail() {
  pushd tdrs-backend/plg/promtail
  CONFIG=config.yml
  yq eval -i ".scrape_configs[0].job_name = \"system-$backend_app_name\""  $CONFIG
  yq eval -i ".scrape_configs[0].static_configs[0].labels.job = \"system-$backend_app_name\""  $CONFIG
  yq eval -i ".scrape_configs[1].job_name = \"backend-$backend_app_name\""  $CONFIG
  yq eval -i ".scrape_configs[1].static_configs[0].labels.job = \"backend-$backend_app_name\""  $CONFIG
  popd
}

update_backend()
{
    cd tdrs-backend || exit
    #cf unset-env "$CGAPPNAME_BACKEND" "AV_SCAN_URL"

    if [ "$CF_SPACE" = "tanf-prod" ]; then
    echo ''
      #cf set-env "$CGAPPNAME_BACKEND" AV_SCAN_URL "http://tanf-prod-clamav-rest.apps.internal:9000/scan"
    else   
     echo ''
      # Add environment varilables for clamav
      #cf set-env "$CGAPPNAME_BACKEND" AV_SCAN_URL "http://tdp-clamav-nginx-$env.apps.internal:9000/scan"

      # Add variable for dev/staging apps to know their DB name. Prod uses default AWS name.
      #cf unset-env "$CGAPPNAME_BACKEND" "APP_DB_NAME"
      #cf set-env "$CGAPPNAME_BACKEND" "APP_DB_NAME" "tdp_db_$backend_app_name"
    fi

    if [ ! "$1" = "rolling" ] ; then
        #cf push "$CGAPPNAME_BACKEND" --no-route -f manifest.buildpack.yml -t 180
        # set up JWT key if needed
        if cf e "$CGAPPNAME_BACKEND" | grep -q JWT_KEY ; then
            echo jwt cert already created
        else
            generate_jwt_cert
        fi
    fi

    #cf map-route "$CGAPPNAME_BACKEND" apps.internal --hostname "$CGAPPNAME_BACKEND"

    # Add network policy to allow frontend to access backend
    #cf add-network-policy "$CGAPPNAME_FRONTEND" "$CGAPPNAME_BACKEND" --protocol tcp --port 8080

    if [ "$CF_SPACE" = "tanf-prod" ]; then
      # Add network policy to allow backend to access tanf-prod services
      #cf add-network-policy "$CGAPPNAME_BACKEND" clamav-rest --protocol tcp --port 9000
          echo ''

    else
      #cf add-network-policy "$CGAPPNAME_BACKEND" tdp-clamav-nginx-$env --protocol tcp --port 9000
          echo ''

    fi

    cd ..
}

bind_backend_to_services() {
    echo "Binding services to app: $CGAPPNAME_BACKEND"

    if [ "$CGAPPNAME_BACKEND" = "tdp-backend-develop" ]; then
      # TODO: this is technical debt, we should either make staging mimic tanf-dev
      #       or make unique services for all apps but we have a services limit
      #       Introducing technical debt for release 3.0.0 specifically.
      env="develop"
    fi

    #cf bind-service "$CGAPPNAME_BACKEND" "tdp-staticfiles-${env}"
    #cf bind-service "$CGAPPNAME_BACKEND" "tdp-datafiles-${env}"
    #cf bind-service "$CGAPPNAME_BACKEND" "tdp-db-${env}"

    # Setting up the ElasticSearch service
    #cf bind-service "$CGAPPNAME_BACKEND" "es-${env}"

    echo "Restarting app: $CGAPPNAME_BACKEND"
    #cf restage "$CGAPPNAME_BACKEND"

}

##############################
# Main script body
##############################

# Determine the appropriate BASE_URL for the deployed instance based on the
# provided Cloud.gov App Name
DEFAULT_ROUTE="https://$CGAPPNAME_FRONTEND.app.cloud.gov"
if [ -n "$BASE_URL" ]; then
  # Use Shell Parameter Expansion to replace localhost in the URL
  echo BASE_URL="\"${BASE_URL//http:\/\/localhost:8080/$DEFAULT_ROUTE}\"" >> $tf_path/env_vars.tfvars
elif [ "$CF_SPACE" = "tanf-prod" ]; then
  # Keep the base url set explicitly for production.
  echo BASE_URL="\"https://tanfdata.acf.hhs.gov/v1\"" >> $tf_path/env_vars.tfvars
elif [ "$CF_SPACE" = "tanf-staging" ]; then
  # use .acf.hss.gov domain for develop and staging.
  echo BASE_URL="\"https://$CGAPPNAME_FRONTEND.acf.hhs.gov/v1\"" >> $tf_path/env_vars.tfvars
else
  # Default to the route formed with the cloud.gov env for the lower environments.
  echo BASE_URL="\"$DEFAULT_ROUTE/v1\"" >> $tf_path/env_vars.tfvars
fi

DEFAULT_FRONTEND_ROUTE="${DEFAULT_ROUTE//backend/frontend}"
if [ -n "$FRONTEND_BASE_URL" ]; then
  echo FRONTEND_BASE_URL="\"${FRONTEND_BASE_URL//http:\/\/localhost:3000/$DEFAULT_FRONTEND_ROUTE}\"" >> $tf_path/env_vars.tfvars
elif [ "$CF_SPACE" = "tanf-prod" ]; then
  # Keep the base url set explicitly for production.
  echo FRONTEND_BASE_URL="\"https://tanfdata.acf.hhs.gov\"" >> $tf_path/env_vars.tfvars
elif [ "$CF_SPACE" = "tanf-staging" ]; then
   # use .acf.hss.gov domain for develop and staging.
  echo FRONTEND_BASE_URL="\"https://$CGAPPNAME_FRONTEND.acf.hhs.gov\"" >> $tf_path/env_vars.tfvars
else
  # Default to the route formed with the cloud.gov env for the lower environments.
  echo FRONTEND_BASE_URL="\"$DEFAULT_FRONTEND_ROUTE\"" >> $tf_path/env_vars.tfvars
fi

echo KIBANA_BASE_URL="\"http://$CGAPPNAME_KIBANA.apps.internal\"" >> $tf_path/env_vars.tfvars

# Dynamically generate a new DJANGO_SECRET_KEY
echo "DJANGO_SECRET_KEY=\"$(python3 -c "from secrets import token_urlsafe; print(token_urlsafe(50))")\"" >> $tf_path/env_vars.tfvars

# Dynamically set DJANGO_CONFIGURATION based on Cloud.gov Space
echo DJANGO_SETTINGS_MODULE=\"tdpservice.settings.cloudgov\" >> $tf_path/env_vars.tfvars
if [ "$CF_SPACE" = "tanf-prod" ]; then
  echo DJANGO_CONFIGURATION=\"Production\" >> $tf_path/env_vars.tfvars
elif [ "$CF_SPACE" = "tanf-staging" ]; then
  echo DJANGO_CONFIGURATION=\"Staging\" >> $tf_path/env_vars.tfvars
else
  echo DJANGO_CONFIGURATION=\"Development\" >> $tf_path/env_vars.tfvars
  echo DJANGO_DEBUG=\"Yes\" >> $tf_path/env_vars.tfvars
  echo CYPRESS_TOKEN=\"$CYPRESS_TOKEN\" >> $tf_path/env_vars.tfvars
fi
echo "" >> $tf_path/env_vars.tfvars

prepare_promtail
if [ "$DEPLOY_STRATEGY" = "rolling" ] ; then
    # Perform a rolling update for the backend and frontend deployments if
    # specified, otherwise perform a normal deployment
    update_backend 'rolling'
elif [ "$DEPLOY_STRATEGY" = "bind" ] ; then
    # Bind the services the application depends on and restage the app.
    bind_backend_to_services
elif [ "$DEPLOY_STRATEGY" = "initial" ]; then
    # There is no app with this name, and the services need to be bound to it
    # for it to work. the app will fail to start once, have the services bind,
    # and then get restaged.
    update_backend
    bind_backend_to_services
elif [ "$DEPLOY_STRATEGY" = "rebuild" ]; then
    # You want to redeploy the instance under the same name
    # Delete the existing app (with out deleting the services)
    # and perform the initial deployment strategy.
    #cf delete "$CGAPPNAME_BACKEND" -r -f
    update_backend
    bind_backend_to_services
else
    # No changes to deployment config, just deploy the changes and restart
    update_backend
fi
