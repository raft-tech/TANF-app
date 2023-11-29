#!/bin/bash

cd ./tdrs-backend

app=${1}
guid=$(cf app --guid $app)

# echo $guid

# requires `jq` - https://jqlang.github.io/jq/download/
app_vars=$(cf curl /v2/apps/$guid/env)

db_creds=$(echo $app_vars | jq -r '.system_env_json.VCAP_SERVICES."aws-rds"[0].credentials')
connection_str=$(echo $db_creds | jq -r '[.host, .port]' | jq -r 'join(":")')

echo "Starting tunnel..."
cf ssh -N -L 5432:$connection_str $app &
sleep 5
echo "Done."

cp ./.env.example ./.env.ci

vcap_services=$(echo $app_vars | jq -r '.system_env_json.VCAP_SERVICES')
vcap_application=$(echo $app_vars | jq -rc '.application_env_json.VCAP_APPLICATION')

# replace host env var
fixed_vcap_services=$(echo $vcap_services | jq -rc '."aws-rds"[0].credentials.host="host.docker.internal"')

echo "VCAP_SERVICES=$fixed_vcap_services" >> .env.ci
echo "VCAP_APPLICATION=$vcap_application" >> .env.ci


echo "Starting container..."
docker-compose -f docker-compose.ci.yml --env-file .env.ci up -d
echo "Done."

echo "Applying migrations..."
# stop script and report errors??
docker-compose -f docker-compose.ci.yml exec web python /tdpapp/manage.py migrate
echo "Done."

echo "Cleaning up..."
docker-compose -f docker-compose.ci.yml down -v
kill $!
rm ./.env.ci
cd ..
echo "Done."