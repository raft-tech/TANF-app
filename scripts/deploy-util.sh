# function to check if a service exists
service_exists()
{
  cf service "$1" >/dev/null 2>&1
}


# Performs a normal deployment unless rolling is specified in the fucntion call
update_frontend()
{
  cd tdrs-frontend && npm run dist && cd ..
	if [ "$1" = "rolling" ] ; then
		# Do a zero downtime deploy.  This requires enough memory for
		# two apps to exist in the org/space at one time.
		cf push $CGHOSTNAME_FRONTEND --no-route -f tdrs-frontend/manifest.yml --strategy rolling || exit 1
	else
		cf push $CGHOSTNAME_FRONTEND --no-route -f tdrs-frontend/manifest.yml
	fi
	cf map-route $CGHOSTNAME_FRONTEND app.cloud.gov --hostname "${CGHOSTNAME_FRONTEND}"
}

# Performs a normal deployment unless rolling is specified in the fucntion call
update_backend()
{
	if [ "$1" = "rolling" ] ; then
		# Do a zero downtime deploy.  This requires enough memory for
		# two apps to exist in the org/space at one time.
		cf push $CGHOSTNAME_BACKEND --no-route -f tdrs-backend/manifest.yml  --strategy rolling || exit 1

	else
		cf push $CGHOSTNAME_BACKEND --no-route -f tdrs-backend/manifest.yml
		# set up JWT key if needed
		if cf e $CGHOSTNAME_BACKEND | grep -q JWT_KEY ; then
		   echo jwt cert already created
		else
		   generate_jwt_cert
	   fi
	fi
	cf map-route $CGHOSTNAME_BACKEND app.cloud.gov --hostname "$CGHOSTNAME_BACKEND"
}
