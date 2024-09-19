#!/bin/sh

# source deploy-util.sh

# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

#The application name  defined via the manifest yml for the frontend
CGHOSTNAME_FRONTEND=${2}
CGHOSTNAME_BACKEND=${3}
CGAPPNAME_KIBANA=${4}
CF_SPACE=${5}
ENVIRONMENT=${6}

env=${CF_SPACE#"tanf-"}
frontend_app_name=$(echo $CGHOSTNAME_FRONTEND | cut -d"-" -f3)

# Update the Kibana name to include the environment
KIBANA_BASE_URL="${CGAPPNAME_KIBANA}-${env}.apps.internal"

prepare_promtail() {
  pushd tdrs-frontend
  CONFIG=promtail.config.yml
  yq eval -i ".scrape_configs[0].job_name = \"system-$backend_app_name\""  $CONFIG
  yq eval -i ".scrape_configs[1].job_name = \"backend-$backend_app_name\""  $CONFIG
  popd
}

update_frontend()
{
    echo DEPLOY_STRATEGY: "$DEPLOY_STRATEGY"
    echo FRONTEND_HOST: "$CGHOSTNAME_FRONTEND"
    echo BACKEND_HOST: "$CGHOSTNAME_BACKEND"
    echo KIBANA_BASE_URL: "$KIBANA_BASE_URL"
    cd tdrs-frontend || exit

    if [ "$CF_SPACE" = "tanf-prod" ]; then
        echo "REACT_APP_BACKEND_URL=https://tanfdata.acf.hhs.gov/v1" >> .env.production
        echo "REACT_APP_FRONTEND_URL=https://tanfdata.acf.hhs.gov" >> .env.production
        echo "REACT_APP_BACKEND_HOST=https://tanfdata.acf.hhs.gov" >> .env.production
        echo "REACT_APP_LOGIN_GOV_URL=https://secure.login.gov/" >> .env.production
        echo "REACT_APP_CF_SPACE=$CF_SPACE" >> .env.production
        echo "BACK_END=" >> .env.production
    elif [ "$CF_SPACE" = "tanf-staging" ]; then
        echo "REACT_APP_BACKEND_URL=https://$CGHOSTNAME_FRONTEND.acf.hhs.gov/v1" >> .env.development
        echo "REACT_APP_FRONTEND_URL=https://$CGHOSTNAME_FRONTEND.acf.hhs.gov" >> .env.development
        echo "REACT_APP_BACKEND_HOST=https://$CGHOSTNAME_FRONTEND.acf.hhs.gov" >> .env.development
        echo "REACT_APP_CF_SPACE=$CF_SPACE" >> .env.development

        cf set-env "$CGHOSTNAME_FRONTEND" ALLOWED_ORIGIN "https://$CGHOSTNAME_FRONTEND.acf.hhs.gov"
        cf set-env "$CGHOSTNAME_FRONTEND" CONNECT_SRC '*.acf.hhs.gov'
    else
        echo "REACT_APP_BACKEND_URL=https://$CGHOSTNAME_FRONTEND.app.cloud.gov/v1" >> .env.development
        echo "REACT_APP_FRONTEND_URL=https://$CGHOSTNAME_FRONTEND.app.cloud.gov" >> .env.development
        echo "REACT_APP_BACKEND_HOST=https://$CGHOSTNAME_FRONTEND.app.cloud.gov" >> .env.development
        echo "REACT_APP_CF_SPACE=$CF_SPACE" >> .env.development

        cf set-env "$CGHOSTNAME_FRONTEND" ALLOWED_ORIGIN "https://$CGHOSTNAME_FRONTEND.app.cloud.gov"
        cf set-env "$CGHOSTNAME_FRONTEND" CONNECT_SRC '*.app.cloud.gov'
    fi

    cf set-env "$CGHOSTNAME_FRONTEND" BACKEND_HOST "$CGHOSTNAME_BACKEND"
    cf set-env "$CGHOSTNAME_FRONTEND" KIBANA_BASE_URL "$KIBANA_BASE_URL"

    npm run build:$ENVIRONMENT
    unlink .env.production
    mkdir deployment


    cp -r build deployment/public
    cp nginx/cloud.gov/buildpack.nginx.conf deployment/nginx.conf
    cp nginx/cloud.gov/locations.conf deployment/locations.conf
    cp nginx/cloud.gov/ip_whitelist.conf deployment/ip_whitelist.conf
    cp nginx/cloud.gov/ip_whitelist_ipv4.conf deployment/ip_whitelist_ipv4.conf
    cp nginx/cloud.gov/ip_whitelist_ipv6.conf deployment/ip_whitelist_ipv6.conf
    cp nginx/mime.types deployment/mime.types
    cp nginx/src/503.html deployment/public/503_.html
    cp -r nginx/src/static/ deployment/public/

    cp manifest.buildpack.yml deployment/manifest.buildpack.yml
    cd deployment || exit

    if [ "$1" = "rolling" ] ; then
        # Do a zero downtime deploy.  This requires enough memory for
        # two apps to exist in the org/space at one time.
        cf push "$CGHOSTNAME_FRONTEND" --no-route -f manifest.buildpack.yml --strategy rolling || exit 1
    else
        cf push "$CGHOSTNAME_FRONTEND" --no-route -f manifest.buildpack.yml
    fi

    if [ "$CF_SPACE" = "tanf-prod" ]; then
        cf map-route "$CGHOSTNAME_FRONTEND" tanfdata.acf.hhs.gov
    elif [ "$CF_SPACE" = "tanf-staging" ]; then
        cf map-route "$CGHOSTNAME_FRONTEND" "$CGHOSTNAME_FRONTEND".acf.hhs.gov
    else
        cf map-route "$CGHOSTNAME_FRONTEND" app.cloud.gov --hostname "${CGHOSTNAME_FRONTEND}"
    fi

    cd ../..
    rm -r tdrs-frontend/deployment
}

# perform a rolling update for the backend and frontend deployments if
# specified, otherwise perform a normal deployment
prepare_promtail
if [ "$DEPLOY_STRATEGY" = "rolling" ] ; then
    update_frontend 'rolling'
else
    update_frontend
fi
