#!/usr/bin/env bash

# export REDIS_URI=rediss://xtJnXoZpeLNID24pQhpPb9HSr@master.prd-3fa9afec-b332-43c8-9a46-0aaa72c49d53.pw1qnn.usgw1.cache.amazonaws.com:6379
echo starting celery
celery -A tdpservice.settings worker -c 1 &
sleep 5
# TODO: Uncomment the following line to add flower service when memory limitation is resolved
echo "REDIS_URI: $REDIS_URI"
celery -A tdpservice.settings --broker=$REDIS_URI flower &
celery -A tdpservice.settings beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &
