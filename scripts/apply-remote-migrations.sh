#!/bin/bash

cd ./tdrs-backend

app=tdp-backend-raft
guid=$(cf app --guid $app)

echo $guid

# requires `jq` - https://jqlang.github.io/jq/download/
creds=$(cf curl /v2/apps/$guid/env | jq -r '.system_env_json.VCAP_SERVICES."aws-rds"[0].credentials')
connection_str=$(echo $creds | jq -r '[.host, .port]' | jq -r 'join(":")')

echo $connection_str
# echo $creds

echo "Starting tunnel..."
cf ssh -N -L 5432:$connection_str $app &
sleep 5
echo "Done."

cp ./.env.example ./.env.ci

echo "DB_NAME=$(echo $creds | jq -r '.name')" >> ./.env.ci # usually needs to be a different valuec
echo "DB_HOST=host.docker.internal" >> ./.env.ci
echo "DB_PORT=$(echo $creds | jq -r '.port')" >> ./.env.ci
echo "DB_USER=$(echo $creds | jq -r '.username')" >> ./.env.ci
echo "DB_PASSWORD=$(echo $creds | jq -r '.password')" >> ./.env.ci


echo "Starting container..."
# docker-compose -f ./tdrs-backend/docker-compose.ci.yml --env-file ./tdrs-backend/.env.ci up -d
docker-compose -f docker-compose.ci.yml --env-file .env.ci up -d
# some sort of `docker run` would likely be preferable here
# docker build -t web:ci .
# docker run -itd --name web --add-host=host.docker.internal:host-gateway web:ci
echo "Done."

echo "Applying migrations..."
# docker-compose -f ./tdrs-backend/docker-compose.ci.yml exec web python manage.py migrate
docker-compose -f docker-compose.ci.yml exec web python manage.py migrate
# docker exec --env-file ./.env.ci web python manage.py migrate
echo "Done."

echo "Cleaning up..."
docker-compose -f docker-compose.ci.yml down -v
# docker stop web
# docker rm web
kill $!
# rm ./.env.ci
cd ..
echo "Done."