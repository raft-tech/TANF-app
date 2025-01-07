#!/usr/bin/env bash

backvarspath="./$1/backend_config.tfvars"
echo "backvarspath: $backvarspath"
varspath="./$1/variables.tf"
echo "varspath: $varspath"
envpath="./$1/env_vars.tfvars"
echo "envpath: $envpath"

if [[ $# -eq 0 ]] ; then
    echo 'You need to pass the env you are configuring: 'dev', 'staging', 'production'.'
    exit 1
fi

if [[ "$1" != "dev" && "$1" != "staging" && "$1" != "production" ]] ; then
  echo 'The first argument to this script must be one of: 'dev', 'staging', or 'production'.'
  exit 1
fi

S3_CREDENTIALS=$(cf service-key tdp-tf-states tdp-tf-key | tail -n +2)
if [ -z "$S3_CREDENTIALS" ]; then
  echo "Unable to get service-keys, you may need to login to Cloud.gov first"
  echo "Run cf login --sso and attempt to retry running this script"
  exit 1
fi

{
  echo "access_key = \"$(echo "${S3_CREDENTIALS}" | jq -r .access_key_id)\""
  echo "secret_key = \"$(echo "${S3_CREDENTIALS}" | jq -r .secret_access_key)\""
  echo "region = \"$(echo "${S3_CREDENTIALS}" | jq -r '.region')\""
  echo "bucket = \"$(echo "${S3_CREDENTIALS}" | jq -r '.bucket')\""
} >> $backvarspath

exit 1
set_backend_vars() {
  var_list=(
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
  "KIBANA_BASE_URL"
  "LOGGING_LEVEL"
  "REDIS_URI"
  "JWT_KEY"
  "SENDGRID_API_KEY"
  )

  for var_name in ${var_list[@]}; do
    var_value=${!var_name}

    echo "\nvariable \"${var_name}\" {
      type        = string
      description = \"\"
    }" >> $varspath

    if [[ ("$CF_SPACE" = "tanf-staging") ]]; then
        staging_var="STAGING_$var_name"
        if [[ "${!staging_var}" ]]; then
          var_value=${!staging_var}
        fi
    elif [[ -z "${!var_name}" ]]; then
        echo "WARNING: Empty value for $var_name."
        continue
    fi

    echo "${var_name} = \"${var_value}\""  >> $envpath
  done
}

set_backend_vars
