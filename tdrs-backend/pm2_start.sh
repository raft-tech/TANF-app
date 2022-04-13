#!/usr/bin/env bash
set -e
echo "pipenv install"
pipenv install --skip-lock --dev --system
echo "python manage.py collectstatic --noinput"
python manage.py collectstatic --noinput

echo "Applying database migrations"
python manage.py makemigrations
python manage.py migrate
python manage.py populate_stts
python manage.py collectstatic --noinput
./wait_for_services.sh && python ./manage.py runserver 0.0.0.0:8080
