#!/bin/sh

# source deploy-util.sh

# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

#The application name  defined via the manifest yml for the frontend
CGAPPNAME_FRONTEND=${2}
CGAPPNAME_BACKEND=${3}
CF_SPACE=${4}

update_frontend()
{
    echo DEPLOY_STRATEGY: "$DEPLOY_STRATEGY"
    echo FRONTEND_HOST: "$CGAPPNAME_FRONTEND"
    echo BACKEND_HOST: "$CGAPPNAME_BACKEND"
    cd tdrs-frontend || exit
    if [ "$CF_SPACE" = "tanf-prod" ]; then
        echo "REACT_APP_BACKEND_URL=https://api-tanfdata.acf.hhs.gov/v1" >> .env.production
        echo "REACT_APP_BACKEND_HOST=https://api-tanfdata.acf.hhs.gov" >> .env.production
        echo "REACT_APP_CF_SPACE=$CF_SPACE" >> .env.production

        # For nginx to allow cross origin requests from the resources that it serves
        # NOT a frontend var
        cf set-env "$CGAPPNAME_FRONTEND" ALLOWED_ORIGIN 'https://tanfdata.acf.hhs.gov'
        cf set-env "$CGAPPNAME_FRONTEND" CONNECT_SRC '*.acf.hhs.gov'
    else
        echo "REACT_APP_BACKEND_URL=https://$CGAPPNAME_BACKEND.app.cloud.gov/v1" >> .env.development
        echo "REACT_APP_BACKEND_HOST=https://$CGAPPNAME_BACKEND.app.cloud.gov" >> .env.development
        echo "REACT_APP_CF_SPACE=$CF_SPACE" >> .env.development

        cf set-env "$CGAPPNAME_FRONTEND" ALLOWED_ORIGIN "https://$CGAPPNAME_FRONTEND.app.cloud.gov"
        cf set-env "$CGAPPNAME_FRONTEND" CONNECT_SRC '*.app.cloud.gov'
    fi
    npm run build
    unlink .env.production
    mkdir deployment

    cp -r build deployment/public
    cp nginx/buildpack.nginx.conf deployment/nginx.conf
    cp nginx/locations.conf deployment/locations.conf
    cp nginx/mime.types deployment/mime.types

    cp manifest.buildpack.yml deployment/manifest.buildpack.yml
    cd deployment || exit

    if [ "$1" = "rolling" ] ; then
        # Do a zero downtime deploy.  This requires enough memory for
        # two apps to exist in the org/space at one time.
        cf push "$CGAPPNAME_FRONTEND" --no-route -f manifest.buildpack.yml --strategy rolling || exit 1
    else
        cf push "$CGAPPNAME_FRONTEND" --no-route -f manifest.buildpack.yml
    fi

    cf map-route "$CGAPPNAME_FRONTEND" app.cloud.gov --hostname "${CGAPPNAME_FRONTEND}"
    cd ../..
    rm -r tdrs-frontend/deployment
}

# perform a rolling update for the backend and frontend deployments if
# specified, otherwise perform a normal deployment
if [ "$DEPLOY_STRATEGY" = "rolling" ] ; then
    update_frontend 'rolling'
else
    update_frontend
fi
