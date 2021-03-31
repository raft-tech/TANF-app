
#!/bin/sh


# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

# The environment in which you want to execute these commands
DEPLOY_ENV=${2}

#The application name  defined via the manifest yml for the frontend
CGHOSTNAME_BACKEND=${3}

#The Github Branch triggered to execure this script if triggered in circleci
CIRCLE_BRANCH=${4}

echo DEPLOY_STRATEGY: $DEPLOY_STRATEGY
echo DEPLOY_ENV=$DEPLOY_ENV
echo BACKEND_HOST: $CGHOSTNAME_BACKEND
echo CIRCLE_BRANCH=$CIRCLE_BRANCH

update_backend()
{
    cd tdrs-backend
	  if [ "$1" = "rolling" ] ; then
		    # Do a zero downtime deploy.  This requires enough memory for
		    # two apps to exist in the org/space at one time.
		    cf push $CGHOSTNAME_BACKEND --no-route -f manifest.yml  --strategy rolling || exit 1

	  else
		    cf push $CGHOSTNAME_BACKEND --no-route -f manifest.yml
		    # set up JWT key if needed
		    if cf e $CGHOSTNAME_BACKEND | grep -q JWT_KEY ; then
		        echo jwt cert already created
		    else
		        generate_jwt_cert
	      fi
	  fi
	  cf map-route $CGHOSTNAME_BACKEND app.cloud.gov --hostname "$CGHOSTNAME_BACKEND"
    cd ..
}


# perform a rolling update for the backend and frontend deployments if specifed,
# otherwise perform a normal deployment 
if [ $DEPLOY_STRATEGY = "rolling" ] ; then
	  update_backend 'rolling'
elif [ $DEPLOY_STRATEGY = "bind"] ; then
    update_backend
		cf bind-service $CGHOSTNAME_BACKEND tdp-django-static-sandbox
		cf bind-service $CGHOSTNAME_BACKEND tdp-storage-sandbox
		cf bind-service $CGHOSTNAME_BACKEND tanf-storage
		cf bind-service $CGHOSTNAME_BACKEND tdp-db
		cf restage $CGHOSTNAME_BACKEND
else 
	  update_backend
fi
