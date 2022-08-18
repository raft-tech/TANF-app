#!/usr/bin/env bash
# Apply database migrations

set -e

export LD_LIBRARY_PATH=/home/vcap/deps/0/lib/:/home/vcap/deps/1/lib:$LD_LIBRARY_PATH
( cd  /home/vcap/deps/0/bin/; ./redis-server &)

echo "Applying database migrations"
python manage.py makemigrations
python manage.py migrate
python manage.py populate_stts
python manage.py collectstatic --noinput

celery -A tdpservice.settings worker -l info -c 3 --max-memory-per-child 1024 &

echo "Starting Gunicorn"
if [[ "$DJANGO_CONFIGURATION" = "Development" || "$DJANGO_CONFIGURATION" = "Local" ]]; then
    gunicorn_params="--bind 0.0.0.0:8080 --timeout 10 --workers 3 --reload --log-level $LOGGING_LEVEL"
else
    gunicorn_params="--bind 0.0.0.0:8080 --timeout 10 --workers 3 --log-level $LOGGING_LEVEL"
fi

gunicorn_cmd="gunicorn tdpservice.wsgi:application $gunicorn_params"

exec $gunicorn_cmd