#!/bin/bash
set -e

help() {
    echo "Deploy Keycloak to the Cloud Foundry space you're currently authenticated in."
    echo "Syntax: deploy.sh [-h | -e <dev|staging|prod> -d <service name> -a <admin username> -p <admin password>]"
    echo "Options:"
    echo "h     Print this help message."
    echo "e     The environment to deploy to (required). Must be one of: 'dev', 'staging', or 'prod'."
    echo "d     The Cloud Foundry service name of the RDS instance. REQUIRED."
    echo "a     The admin username to configure for Keycloak. REQUIRED."
    echo "p     The admin password to configure for Keycloak. REQUIRED."
    echo "c     The name of the app that is bound to the same RDS instance that Keycloak will be (e.g. tdp-backend-raft). This is REQUIRED to set environment variables on the docker container since the container doesn't have access to templating tools."
    echo
}

deploy_keycloak_proxy() {
    pushd nginx/cloudgov
    ENV=$1
    KEYCLOAK_APP_NAME="keycloak-$ENV"
    PROXY_HOSTNAME="$KEYCLOAK_APP_NAME"
    PROXY_NAME="keycloak-proxy-$ENV"
    cf push $PROXY_NAME --no-route -f manifest.yml -t 180  --strategy rolling
    cf map-route $PROXY_NAME app.cloud.gov --hostname $PROXY_HOSTNAME
    cf add-network-policy $PROXY_NAME $KEYCLOAK_APP_NAME
    popd
}

deploy_keycloak() {
    pushd app

    MANIFEST=manifest.tmp.yml
    cp manifest.yml $MANIFEST

    ENV=$1
    DB_SERVICE_NAME=$2
    KC_ADMIN_USERNAME=$3
    KC_ADMIN_PASSWORD=$4
    HELPER_APP_NAME=$5

    KEYCLOAK_APP_NAME="keycloak-$ENV"

    VCAP_SERVICES=$(cf env $HELPER_APP_NAME | sed -n '/VCAP_SERVICES/,/VCAP_APPLICATION/p' | sed '$d' | sed '1s/VCAP_SERVICES: //' | sed '1s;^;{\n  \"VCAP_SERVICES\": ;' | sed '$s/$/}/' | jq .VCAP_SERVICES)
    DB_HOST=$(echo $VCAP_SERVICES | jq -r '."aws-rds"[0].credentials.host')
    DB_PORT=$(echo $VCAP_SERVICES | jq -r '."aws-rds"[0].credentials.port')
    DB_PASSWORD=$(echo $VCAP_SERVICES | jq -r '."aws-rds"[0].credentials.password')
    DB_USERNAME=$(echo $VCAP_SERVICES | jq -r '."aws-rds"[0].credentials.username')

    yq eval -i ".applications[0].env.KC_BOOTSTRAP_ADMIN_USERNAME = \"$KC_ADMIN_USERNAME\""  $MANIFEST
    yq eval -i ".applications[0].env.KC_BOOTSTRAP_ADMIN_PASSWORD = \"$KC_ADMIN_PASSWORD\""  $MANIFEST
    yq eval -i ".applications[0].env.KC_HOSTNAME = \"https://$KEYCLOAK_APP_NAME.app.cloud.gov\""  $MANIFEST
    yq eval -i ".applications[0].env.KC_DB_URL = \"jdbc:postgresql://$DB_HOST:$DB_PORT/keycloak\""  $MANIFEST
    yq eval -i ".applications[0].env.KC_DB_USERNAME = \"$DB_USERNAME\""  $MANIFEST
    yq eval -i ".applications[0].env.KC_DB_PASSWORD = \"$DB_PASSWORD\""  $MANIFEST
    yq eval -i ".applications[0].services[0] = \"$DB_SERVICE_NAME\""  $MANIFEST

    cf push $KEYCLOAK_APP_NAME --no-route -f $MANIFEST -t 180  --strategy rolling
    cf map-route $KEYCLOAK_APP_NAME apps.internal --hostname $KEYCLOAK_APP_NAME

    rm $MANIFEST
    popd
}

err_help_exit() {
    echo $1
    echo
    help
    popd
    exit
}

pushd "$(dirname "$0")"

while getopts ":he:d:a:p:c:" option; do
   case $option in
      h) # display Help
         help
         exit;;
      e) # The environment to deploy to (required)
         ENV=$OPTARG;;
      d) # Bind a Keycloak to the RDS Instance (required)
         DB_SERVICE_NAME=$OPTARG;;
      a) # The admin username to configure for Keycloak (required)
         KC_ADMIN_USERNAME=$OPTARG;;
      p) # The admin password to configure for Keycloak (required)
         KC_ADMIN_PASSWORD=$OPTARG;;
      c) # The app name to get DB creds from
         HELPER_APP_NAME=$OPTARG;;
      \?) # Invalid option
         err_help_exit "Error: Invalid option";;
   esac
done

if [ "$#" -eq 0 ]; then
    help
    exit
fi


if [ "$ENV" == "" ]; then
    err_help_exit "Error: you must specify an environment: 'dev', 'staging', or 'prod'."
fi
if [ "$DB_SERVICE_NAME" == "" ]; then
    err_help_exit "Error: you must include a database service name."
fi
if [ "$KC_ADMIN_USERNAME" == "" ]; then
    err_help_exit "Error: you must include an admin username for Keycloak."
fi
if [ "$KC_ADMIN_PASSWORD" == "" ]; then
    err_help_exit "Error: you must include an admin password for Keycloak."
fi
if [ "$HELPER_APP_NAME" == "" ]; then
    err_help_exit "Error: you must include the name of a helper app to get database credentials from for Keycloak."
fi

deploy_keycloak $ENV $DB_SERVICE_NAME $KC_ADMIN_USERNAME $KC_ADMIN_PASSWORD $HELPER_APP_NAME
deploy_keycloak_proxy $ENV
