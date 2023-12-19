#!/usr/bin/env bash

echo starting celery
celery -A tdpservice.settings worker -c 1 &
sleep 5
# TODO: Uncomment the following line to add flower service when memory limitation is resolved
echo "REDIS_URI: $REDIS_URI"
celery -A tdpservice.settings --broker=$REDIS_URI flower &
celery -A tdpservice.settings beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &
