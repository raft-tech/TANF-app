#!/usr/bin/env bash
# Apply database migrations
set -e

echo "Applying database migrations"
python manage.py migrate
#python manage.py populate_stts
#python manage.py collectstatic --noinput

celery -A tdpservice.settings worker -c 1 &
sleep 5
# TODO: Uncomment the following line to add flower service when memory limitation is resolved
celery -A tdpservice.settings --broker=$REDIS_URI flower &
celery -A tdpservice.settings beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &

echo "Starting Gunicorn"
if [[ "$DJANGO_CONFIGURATION" = "Development" || "$DJANGO_CONFIGURATION" = "Local" ]]; then
    gunicorn_params="-c gunicorn_dev_cfg.py"
else
    gunicorn_params="-c gunicorn_prod_cfg.py"
fi

gunicorn_cmd="gunicorn $gunicorn_params"

exec $gunicorn_cmd
