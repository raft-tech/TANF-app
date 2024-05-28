#!/bin/bash

# pipefail is needed to correctly carry over the exit code from zap-full-scan.py
set -uxo pipefail


TARGET_ENV=$1

PROJECT_SLUG=$CIRCLE_PROJECT_USERNAME/$CIRCLE_PROJECT_REPONAME
# These environment variables are exported to Circle CI's BASH_ENV
# by the zap-scanner.sh script for each respective app target.
CMD_ARGS=(
    "$CIRCLE_BUILD_NUM"
    --backend-pass-count "${ZAP_BACKEND_PASS_COUNT:-0}"
    --backend-warn-count "${ZAP_BACKEND_WARN_COUNT:-0}"
    --backend-fail-count "${ZAP_BACKEND_FAIL_COUNT:-0}"
    --frontend-pass-count "${ZAP_FRONTEND_PASS_COUNT:-0}"
    --frontend-warn-count "${ZAP_FRONTEND_WARN_COUNT:-0}"
    --frontend-fail-count "${ZAP_FRONTEND_FAIL_COUNT:-0}"
    --project-slug "$PROJECT_SLUG"
)
echo $CMD_ARGS
# Evaluate the full command before passing it in so it doesn't
# get improperly interpolated by Cloud.gov.
CMD="python manage.py process_owasp_scan ${CMD_ARGS[*]}"
echo $CMD

echo "Starting tunnel..."
cf ssh -N -L tdp-backend-$TARGET_ENV &
sleep 5
echo "Done."

echo Executing process_owasp_scan
$CMD
status=$?
echo Done.

echo "Cleaning up..."
deactivate
kill $!
echo "Done."

if [ $status -eq 0 ]
then
    echo "process_owasp_scan ran successfully."
    exit 0
else
    echo "process_owasp_scan failed."
    exit $status
fi
