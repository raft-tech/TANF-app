#!/bin/sh
#
# This script will attempt to create the services required
# and then launch everything.
#

# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

# The environment in which you want to execute these commands
DEPLOY_ENV=${2}

#The application name  defined via the manifest yml for the backend
CGHOSTNAME_BACKEND=${3}

#The application name  defined via the manifest yml for the frontend
CGHOSTNAME_FRONTEND=${4}


#The Github Branch triggered to execure this script if triggered in circleci
CIRCLE_BRANCH=${7}

echo DEPLOY_STRATEGY: $DEPLOY_STRATEGY
echo DEPLOY_ENV=$DEPLOY_ENV
echo BACKEND_HOST: $CGHOSTNAME_BACKEND
echo FRONTEND_HOST: $CGHOSTNAME_FRONTEND
echo CIRCLE_BRANCH=$CIRCLE_BRANCH


# function to check if a service exists
service_exists()
{
  cf service "$1" >/dev/null 2>&1
}


