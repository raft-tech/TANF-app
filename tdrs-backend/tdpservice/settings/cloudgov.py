"""Define settings classes available for environments deployed in Cloud.gov."""

import json
import os
from requests_aws4auth import AWS4Auth
from elasticsearch import RequestsHttpConnection

from tdpservice.settings.common import Common
import logging

logger = logging.getLogger(__name__)

def get_json_env_var(variable_name):
    """Retrieve and serialize a JSON environment variable."""
    return json.loads(
        os.getenv(variable_name, '{}')
    )


def get_cloudgov_service_creds_by_instance_name(services, instance_name):
    """Retrieve credentials for a bound Cloud.gov service by instance name."""
    return next(
        (service.get('credentials', {}) for service in services
         if service.get('instance_name') == instance_name),
        {}
    )


class CloudGov(Common):
    """Base settings class for applications deployed in Cloud.gov."""

    ############################################################################
    # Variables defined in this section (denoted by a lower-case variable name)
    # will *NOT* get exposed via django.conf.settings
    # Ref: https://docs.djangoproject.com/en/3.2/topics/settings/#creating-your-own-settings  # noqa

    # Cloud.gov exposes variables for the application and bound services via
    # VCAP_APPLICATION and VCAP_SERVICES environment variables, respectively.
    cloudgov_app = get_json_env_var('VCAP_APPLICATION')
    APP_NAME = cloudgov_app.get('application_name')

    cloudgov_services = get_json_env_var('VCAP_SERVICES')

    cloudgov_space = cloudgov_app.get('space_name', 'tanf-dev')
    cloudgov_space_suffix = cloudgov_space.strip('tanf-')
    cloudgov_name = cloudgov_app.get('name').split("-")[-1]  # converting "tdp-backend-name" to just "name"
    services_basename = cloudgov_name if (
        cloudgov_name == "develop" and cloudgov_space_suffix == "staging"
    ) else cloudgov_space_suffix

    database_creds = get_cloudgov_service_creds_by_instance_name(
        cloudgov_services['aws-rds'],
        f'tdp-db-{services_basename}'
    )
    s3_datafiles_creds = get_cloudgov_service_creds_by_instance_name(
        cloudgov_services['s3'],
        f'tdp-datafiles-{services_basename}'
    )
    s3_staticfiles_creds = get_cloudgov_service_creds_by_instance_name(
        cloudgov_services['s3'],
        f'tdp-staticfiles-{services_basename}'
    )

    ############################################################################

    INSTALLED_APPS = (*Common.INSTALLED_APPS, 'gunicorn')

    ###
    # Dynamic Database configuration based on cloud.gov services
    #
    env_based_db_name = f'tdp_db_{cloudgov_space_suffix}_{cloudgov_name}'

    db_name = database_creds['db_name'] if (cloudgov_space_suffix in ["prod",  "staging"]) else env_based_db_name

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_name,
            'USER': database_creds['username'],
            'PASSWORD': database_creds['password'],
            'HOST': database_creds['host'],
            'PORT': database_creds['port']
        }
    }

    # Username or email for initial Django Super User
    DJANGO_SUPERUSER_NAME = os.getenv(
        'DJANGO_SU_NAME',
        'alexandra.pennington@acf.hhs.gov'
    )

    # Localstack is always disabled in a cloud.gov environment
    USE_LOCALSTACK = False

    ###
    # Store user uploaded data files in designated S3
    #
    DEFAULT_FILE_STORAGE = 'tdpservice.backends.DataFilesS3Storage'
    AWS_S3_DATAFILES_ACCESS_KEY = s3_datafiles_creds['access_key_id']
    AWS_S3_DATAFILES_SECRET_KEY = s3_datafiles_creds['secret_access_key']
    AWS_S3_DATAFILES_BUCKET_NAME = s3_datafiles_creds['bucket']
    AWS_S3_DATAFILES_ENDPOINT = f'https://{s3_datafiles_creds["endpoint"]}'
    AWS_S3_DATAFILES_REGION_NAME = s3_datafiles_creds['region']

    ###
    # Store files generated by collectstatic for the admin site in designated S3
    #
    STATICFILES_STORAGE = 'tdpservice.backends.StaticFilesS3Storage'
    AWS_S3_STATICFILES_ACCESS_KEY = s3_staticfiles_creds['access_key_id']
    AWS_S3_STATICFILES_SECRET_KEY = s3_staticfiles_creds['secret_access_key']
    AWS_S3_STATICFILES_BUCKET_NAME = s3_staticfiles_creds['bucket']
    AWS_S3_STATICFILES_ENDPOINT = f'https://{s3_staticfiles_creds["endpoint"]}'
    AWS_S3_STATICFILES_REGION_NAME = s3_staticfiles_creds['region']

    MEDIA_URL = \
        f'{AWS_S3_STATICFILES_ENDPOINT}/{AWS_S3_STATICFILES_BUCKET_NAME}/{APP_NAME}/'

    # https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/http-caching#cache-control
    # Response can be cached by browser and any intermediary caches
    # (i.e. it is "public") for up to 1 day
    # 86400 = (60 seconds x 60 minutes x 24 hours)
    # TODO: Determine if this is still necessary
    AWS_HEADERS = {
        "Cache-Control": "max-age=86400, s-maxage=86400, must-revalidate",
    }
    # The following variables are used to configure the Django Elasticsearch
    es_access_key = cloudgov_services['aws-elasticsearch'][0]['credentials']['access_key']
    es_secret_key = cloudgov_services['aws-elasticsearch'][0]['credentials']['secret_key']
    es_host = cloudgov_services['aws-elasticsearch'][0]['credentials']['uri']

    awsauth = AWS4Auth(
        es_access_key,
        es_secret_key,
        'us-gov-west-1',
        'es'
    )

    # Elastic
    ELASTICSEARCH_DSL = {
        'default': {
            'hosts': es_host,
            'http_auth': awsauth,
            'use_ssl': True,
            'connection_class': RequestsHttpConnection,
        },
    }


class Development(CloudGov):
    """Settings for applications deployed in the Cloud.gov dev space."""

    # https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = ['.app.cloud.gov']


class Staging(CloudGov):
    """Settings for applications deployed in the Cloud.gov staging space."""

    ALLOWED_HOSTS = [
        'tdp-frontend-staging.acf.hhs.gov',
        'tdp-frontend-develop.acf.hhs.gov'
        ]

    LOGIN_GOV_CLIENT_ID = os.getenv(
        'OIDC_RP_CLIENT_ID',
        'urn:gov:gsa:openidconnect.profiles:sp:sso:hhs:tanf-proto-staging'
    )

class Production(CloudGov):
    """Settings for applications deployed in the Cloud.gov production space."""

    # TODO: Add production ACF domain when known
    ALLOWED_HOSTS = ['tanfdata.acf.hhs.gov', 'tdp-frontend-prod.app.cloud.gov']

    LOGIN_GOV_CLIENT_ID = os.getenv(
        'OIDC_RP_CLIENT_ID',
        'urn:gov:gsa:openidconnect.profiles:sp:sso:hhs:tanf-prod'
    )
    ENABLE_DEVELOPER_GROUP = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_DOMAIN = '.acf.hhs.gov'
    SESSION_COOKIE_PATH = "/;HttpOnly"
    MIDDLEWARE = ('tdpservice.middleware.SessionMiddleware', *Common.MIDDLEWARE)

    # CORS allowed origins
    CORS_ALLOWED_ORIGINS = ['https://tanfdata.acf.hhs.gov']
