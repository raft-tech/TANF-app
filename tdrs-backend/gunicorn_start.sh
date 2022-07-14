#!/usr/bin/env bash
# Apply database migrations
set -e

echo "Starting Celery"
celery -A tdpservice.scheduling worker -l info &
celery -A tdpservice.scheduling beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &

echo "Applying database migrations"
python manage.py makemigrations
python manage.py migrate
python manage.py populate_stts
python manage.py collectstatic --noinput

echo "Starting Gunicorn"
if [[ "$DJANGO_CONFIGURATION" = "Development" || "$DJANGO_CONFIGURATION" = "Local" ]]; then
    gunicorn_params="--bind 0.0.0.0:8080 --timeout 10 --workers 3 --reload --log-level $LOGGING_LEVEL"
else
    gunicorn_params="--bind 0.0.0.0:8080 --timeout 10 --workers 3 --log-level $LOGGING_LEVEL"
fi

gunicorn_cmd="gunicorn tdpservice.wsgi:application $gunicorn_params"

exec $gunicorn_cmd
