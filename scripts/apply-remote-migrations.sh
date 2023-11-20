#!/bin/bash

app=tdp-backend-raft
guid=$(cf app --guid $app)

echo $guid

# requires `jq` - https://jqlang.github.io/jq/download/
creds=$(cf curl /v2/apps/$guid/env | jq -r '.system_env_json.VCAP_SERVICES."aws-rds"[0].credentials')
connection_str=$(echo $creds | jq -r '[.host, .port]' | jq -r 'join(":")')

# echo $connection_str
# echo $creds

echo "Starting tunnel..."
cf ssh -N -L 5432:$connection_str $app &
echo "Done."

cp ./tdrs-backend/.env ./tdrs-backend/.env.ci

echo "DB_NAME=$(echo $creds | jq -r '.name')" >> ./tdrs-backend/.env.ci # usually needs to be a different value
# echo "DB_HOST=$(echo $creds | jq -r '.host')" >> ./tdrs-backend/.env.ci
echo "DB_PORT=$(echo $creds | jq -r '.port')" >> ./tdrs-backend/.env.ci
echo "DB_USER=$(echo $creds | jq -r '.username')" >> ./tdrs-backend/.env.ci
echo "DB_PASSWORD=$(echo $creds | jq -r '.password')" >> ./tdrs-backend/.env.ci


echo "Starting application..."
docker-compose -f ./tdrs-backend/docker-compose.ci.yml --env-file ./tdrs-backend/.env.ci up -d
echo "Done."

echo "Applying migrations..."
docker-compose -f ./tdrs-backend/docker-compose.ci.yml exec web python manage.py migrate
echo "Done."

echo "Cleaning up..."
docker-compose -f ./tdrs-backend/docker-compose.ci.yml down -v
# kill script pid (?)
echo "Done."