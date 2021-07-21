"""Define settings classes available for environments deployed in Cloud.gov."""

import json
import os

from tdpservice.settings.common import Common


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
    cloudgov_services = get_json_env_var('VCAP_SERVICES')

    cloudgov_space = cloudgov_app.get('space_name', 'tanf-dev')
    cloudgov_space_suffix = cloudgov_space.strip('tanf-')

    database_creds = get_cloudgov_service_creds_by_instance_name(
        cloudgov_services['aws-rds'],
        f'tdp-db-{cloudgov_space_suffix}'
    )
    s3_datafiles_creds = get_cloudgov_service_creds_by_instance_name(
        cloudgov_services['s3'],
        f'tdp-datafiles-{cloudgov_space_suffix}'
    )
    s3_staticfiles_creds = get_cloudgov_service_creds_by_instance_name(
        cloudgov_services['s3'],
        f'tdp-staticfiles-{cloudgov_space_suffix}'
    )
    ############################################################################

    INSTALLED_APPS = (*Common.INSTALLED_APPS, 'gunicorn')

    ###
    # Dynamic Database configuration based on cloud.gov services
    #
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': database_creds['db_name'],
            'USER': database_creds['username'],
            'PASSWORD': database_creds['password'],
            'HOST': database_creds['host'],
            'PORT': database_creds['port']
        }
    }

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
        f'{AWS_S3_STATICFILES_ENDPOINT}/{AWS_S3_STATICFILES_BUCKET_NAME}'

    # https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/http-caching#cache-control
    # Response can be cached by browser and any intermediary caches
    # (i.e. it is "public") for up to 1 day
    # 86400 = (60 seconds x 60 minutes x 24 hours)
    # TODO: Determine if this is still necessary
    AWS_HEADERS = {
        "Cache-Control": "max-age=86400, s-maxage=86400, must-revalidate",
    }


class Development(CloudGov):
    """Settings for applications deployed in the Cloud.gov dev space."""

    # https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = ['.app.cloud.gov']


class Staging(CloudGov):
    """Settings for applications deployed in the Cloud.gov staging space."""

    ALLOWED_HOSTS = ['tdp-backend-staging.app.cloud.gov']


class Production(CloudGov):
    """Settings for applications deployed in the Cloud.gov production space."""

    # TODO: Add production ACF domain when known
    ALLOWED_HOSTS = ['tdp-backend-production.app.cloud.gov']
