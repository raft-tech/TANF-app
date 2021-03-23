#!/bin/sh

source deploy-util.sh

# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

# The environment in which you want to execute these commands
DEPLOY_ENV=${2}

#The application name  defined via the manifest yml for the frontend
CGHOSTNAME_FRONTEND=${3}

#The Github Branch triggered to execure this script if triggered in circleci
CIRCLE_BRANCH=${4}

echo DEPLOY_STRATEGY: $DEPLOY_STRATEGY
echo DEPLOY_ENV=$DEPLOY_ENV
echo BACKEND_HOST: $CGHOSTNAME_BACKEND
echo FRONTEND_HOST: $CGHOSTNAME_FRONTEND
echo CIRCLE_BRANCH=$CIRCLE_BRANCH


# perform a rolling update for the backend and frontend deployments if specifed,
# otherwise perform a normal deployment 
if [ $DEPLOY_STRATEGY = "rolling" ] ; then

	  update_frontend 'rolling'
else
	  update_frontend
fi
