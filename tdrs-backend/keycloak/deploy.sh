#!/bin/bash
set -e

help() {
    echo "Deploy the PLG stack or a Postgres exporter to the Cloud Foundry space you're currently authenticated in."
    echo "Syntax: deploy.sh [-h | -d <service name> -n <hostname> -m <domain> -a <admin username> -p <admin password>]"
    echo "Options:"
    echo "h     Print this help message."
    echo "d     The Cloud Foundry service name of the RDS instance. REQUIRED."
    echo "n     The hostname for Keycloak. REQUIRED."
    echo "a     The admin username to configure for Keycloak. REQUIRED."
    echo "p     The admin password to configure for Keycloak. REQUIRED."
    echo "c     The name of the app that is bound to the same RDS instance that Keycloak will be (e.g. tdp-backend-raft). This is REQUIRE to set environment variables on the docker container since the container doesn't have access to templating tools."
    echo
}

deploy_keycloak() {
    MANIFEST=manifest.tmp.yml
    cp manifest.yml $MANIFEST

    KC_URI="$2.apps.internal"

    VCAP_SERVICES=$(cf env $5 | sed -n '/VCAP_SERVICES/,/VCAP_APPLICATION/p' | sed '$d' | sed '1s/VCAP_SERVICES: //' | sed '1s;^;{\n  \"VCAP_SERVICES\": ;' | sed '$s/$/}/' | jq .VCAP_SERVICES)
    DB_HOST=$(echo $VCAP_SERVICES | jq -r '."aws-rds"[0].credentials.host')
    DB_PORT=$(echo $VCAP_SERVICES | jq -r '."aws-rds"[0].credentials.port')
    DB_PASSWORD=$(echo $VCAP_SERVICES | jq -r '."aws-rds"[0].credentials.password')
    DB_USERNAME=$(echo $VCAP_SERVICES | jq -r '."aws-rds"[0].credentials.username')

    yq eval -i ".applications[0].name = \"$2\""  $MANIFEST
    yq eval -i ".applications[0].env.KC_BOOTSTRAP_ADMIN_USERNAME = \"$3\""  $MANIFEST
    yq eval -i ".applications[0].env.KC_BOOTSTRAP_ADMIN_PASSWORD = \"$4\""  $MANIFEST
    yq eval -i ".applications[0].env.KC_HOSTNAME = \"$KC_URI\""  $MANIFEST
    yq eval -i ".applications[0].env.KC_DB_URL = \"jdbc:postgresql://$DB_HOST:$DB_PORT/keycloak\""  $MANIFEST
    yq eval -i ".applications[0].env.KC_DB_USERNAME = \"$DB_USERNAME\""  $MANIFEST
    yq eval -i ".applications[0].env.KC_DB_PASSWORD = \"$DB_PASSWORD\""  $MANIFEST
    yq eval -i ".applications[0].services[0] = \"$1\""  $MANIFEST

    # cf push --no-route -f $MANIFEST -t 180  --strategy rolling
    # cf map-route $2 $3 --hostname $KC_HOSTNAME

    # rm $MANIFEST
}

err_help_exit() {
    echo $1
    echo
    help
    popd
    exit
}

pushd "$(dirname "$0")"

while getopts ":hd:n:a:p:c:" option; do
   case $option in
      h) # display Help
         help
         exit;;
      d) # Bind a Keycloak to the RDS Instance (required)
         DB_SERVICE_NAME=$OPTARG;;
      n) # The hostname for Keycloak (required)
         KC_HOSTNAME=$OPTARG;;
      a) # The admin username to configure for Keycloak (required)
         KC_ADMIN=$OPTARG;;
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


if [ "$DB_SERVICE_NAME" == "" ]; then
    err_help_exit "Error: you must include a database service name."
fi
if [ "$KC_HOSTNAME" == "" ]; then
    err_help_exit "Error: you must include a hostname for Keycloak."
fi
if [ "$KC_ADMIN" == "" ]; then
    err_help_exit "Error: you must include an admin username for Keycloak."
fi
if [ "$KC_ADMIN_PASSWORD" == "" ]; then
    err_help_exit "Error: you must include an admin password for Keycloak."
fi
if [ "$HELPER_APP_NAME" == "" ]; then
    err_help_exit "Error: you must include the name of a helper app to get database credentials from for Keycloak."
fi

deploy_keycloak $DB_SERVICE_NAME $KC_HOSTNAME $KC_ADMIN $KC_ADMIN_PASSWORD $HELPER_APP_NAME

popd
