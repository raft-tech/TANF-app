#!/bin/bash

app=${1}

cd ./tdrs-backend

echo "Install dependencies..."
sudo apt install -y gcc
sudo apt install -y graphviz
sudo apt install -y graphviz-dev
sudo apt install -y libpq-dev python3-dev
pip install --upgrade pip pipenv
pipenv install --dev --system --deploy
echo "Done."

echo "Getting credentials..."
guid=$(cf app --guid $app)
app_vars=$(cf curl /v2/apps/$guid/env)

db_creds=$(echo $app_vars | jq -r '.system_env_json.VCAP_SERVICES."aws-rds"[0].credentials')
connection_str=$(echo $db_creds | jq -r '[.host, .port]' | jq -r 'join(":")')
echo "Done."

echo "Starting tunnel..."
cf ssh -N -L 5432:$connection_str $app &
sleep 5
echo "Done."

echo "Setting up environment..."
cp ./.env.example ./.env.ci

vcap_services=$(echo $app_vars | jq -r '.system_env_json.VCAP_SERVICES')
vcap_application=$(echo $app_vars | jq -rc '.application_env_json.VCAP_APPLICATION')

# replace host env var
fixed_vcap_services=$(echo $vcap_services | jq -rc '."aws-rds"[0].credentials.host="host.docker.internal"')

echo "VCAP_SERVICES=$fixed_vcap_services" >> .env.ci
echo "VCAP_APPLICATION=$vcap_application" >> .env.ci

set -a
source .env.ci
export DJANGO_CONFIGURATION=Development
export DJANGO_SETTINGS_MODULE=tdpservice.settings.cloudgov
set +a
echo "Done."

# echo "Starting container..."
# docker-compose -f docker-compose.ci.yml --env-file .env.ci up -d
# pip install wait-for-it
# wait-for-it --service http://web:8080 --timeout 60 -- echo "Docker is ready."
# docker-compose -f docker-compose.ci.yml cp . web:/tdpapp
# docker-compose -f docker-compose.ci.yml restart web
# echo "Done."

echo "Applying migrations..."
# stop script and report errors??
python manage.py migrate
# docker-compose -f docker-compose.ci.yml exec web python /tdpapp/manage.py migrate
echo "Done."

echo "Cleaning up..."
# docker-compose -f docker-compose.ci.yml down -v
# kill $!
# rm ./.env.ci
cd ..
echo "Done."