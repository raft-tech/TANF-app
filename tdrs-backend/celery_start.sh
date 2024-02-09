#!/usr/bin/env bash

echo starting celery
celery -A tdpservice.settings worker -c 3 &
sleep 5
echo "REDIS_URI: $REDIS_URI"
celery -A tdpservice.settings --broker=$REDIS_URI flower --port=8080 &
celery -A tdpservice.settings beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
