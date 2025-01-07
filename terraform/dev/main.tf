###
# Terraform settings and backend
###

terraform {
  required_providers {
    cloudfoundry = {
      source  = "cloudfoundry-community/cloudfoundry"
      version = "0.14.2"
    }
    zipper = {
      source = "ArthurHlt/zipper"
      version = "0.14.0"
    }
  }

  backend "s3" {
    key     = "terraform.tfstate.dev"
    prefix  = var.cf_app_name
    encrypt = true
    region  = "us-gov-west-1"
  }
}

provider "cloudfoundry" {
  api_url      = var.cf_api_url
  user         = var.cf_user
  password     = var.cf_password
  app_logs_max = 30

}

provider "aws" {
  region = var.aws_region
}

###
# Target space/org
###

data "cloudfoundry_space" "space" {
  org_name = var.cf_org_name
  name     = var.cf_space_name
}

###
# Provision RDS instance
###

data "cloudfoundry_service" "rds" {
  name = "aws-rds"
}

resource "cloudfoundry_service_instance" "database" {
  name             = "tdp-db-dev"
  space            = data.cloudfoundry_space.space.id
  service_plan     = data.cloudfoundry_service.rds.service_plans["medium-gp-psql"]
  json_params      = "{\"version\": \"15\", \"storage_type\": \"gp3\", \"storage\": 50}"
  timeouts {
    create = "60m"
    update = "60m"
    delete = "2h"
  }
}

###
# Provision S3 buckets
###

data "cloudfoundry_service" "s3" {
  name = "s3"
}

resource "cloudfoundry_service_instance" "staticfiles" {
  name             = "tdp-staticfiles-dev"
  space            = data.cloudfoundry_space.space.id
  service_plan     = data.cloudfoundry_service.s3.service_plans["basic-public-sandbox"]
}

resource "cloudfoundry_service_instance" "datafiles" {
  name             = "tdp-datafiles-dev"
  space            = data.cloudfoundry_space.space.id
  service_plan     = data.cloudfoundry_service.s3.service_plans["basic-sandbox"]
}

###
# Provision Redis for each env
###

data "cloudfoundry_service" "redis" {
  name = "aws-elasticache-redis"
}

resource "cloudfoundry_service_instance" "redis" {
  for_each     = toset(var.dev_app_names)
  name         = "tdp-redis-${each.value}"
  space        = data.cloudfoundry_space.space.id
  service_plan = data.cloudfoundry_service.redis.service_plans["redis-dev"]
}


###
# Provision elasticsearch
###

data "cloudfoundry_service" "elasticsearch" {
  name = "aws-elasticsearch"
}

resource "cloudfoundry_service_instance" "elasticsearch" {
  name                     = "es-dev"
  space                    = data.cloudfoundry_space.space.id
  service_plan             = data.cloudfoundry_service.elasticsearch.service_plans["es-dev"]
  replace_on_params_change = true
  json_params              = "{\"ElasticsearchVersion\": \"Elasticsearch_7.10\"}"
  timeouts {
    create = "60m"
    update = "60m"
    delete = "2h"
  }
}


provider "zipper" {
  skip_ssl_validation = false
}

resource "zipper_file" "frontend" {
  source = "../../tdrs-frontend/deployment"
  output_path = "../../frontend.zip"
}

resource "cloudfoundry_app" "tdp-frontend-fake" {
    space =  data.cloudfoundry_space.space.id
    for_each = toset(var.test_app_names)
    name = "tdp-frontend-${each.value}"
    buildpack = "https://github.com/cloudfoundry/nginx-buildpack.git#v1.2.6" 
    path = zipper_file.frontend.output_path
    strategy = "v2"
    memory = 256
    disk_quota = 256
    timeout = 180
    environment = {
      "CONNECT_SRC" = "*.app.cloud.gov"
      "ALLOWED_ORIGIN" = "https://tdp-frontend-fake.app.cloud.gov"
    }
}

resource "zipper_file" "backend" {
  source = "../../tdrs-backend"
  output_path = "../../backend.zip"
}

resource "cloudfoundry_app" "tdp-backend-fake" {
    space =  data.cloudfoundry_space.space.id
    for_each = toset(var.test_app_names)
    name = "tdp-backend-${each.value}"
    buildpack = "https://github.com/cloudfoundry/python-buildpack.git#v1.8.3"
    path = zipper_file.backend.output_path
    strategy = "v2"
    command = "./gunicorn_start.sh cloud"
    memory = 2048
    disk_quota = 4096
    timeout = 180
    environment = {
      "DJANGO_SU_NAME" = var.DJANGO_SU_NAME,
      "AV_SCAN_URL" = "http://tdp-clamav-nginx-dev.apps.internal:9000/scan",
      "BASE_URL" = var.BASE_URL,
      "CLAMAV_NEEDED" = var.CLAMAV_NEEDED,
      "CYPRESS_TOKEN" = var.CYPRESS_TOKEN,
      "DJANGO_CONFIGURATION" = var.DJANGO_CONFIGURATION,
      "DJANGO_DEBUG" = var.DJANGO_DEBUG,
      "DJANGO_SETTINGS_MODULE" = var.DJANGO_SETTINGS_MODULE,
      "FRONTEND_BASE_URL" =var.FRONTEND_BASE_URL,
      "AMS_CLIENT_ID" = var.AMS_CLIENT_ID,
      "AMS_CLIENT_SECRET" = var.AMS_CLIENT_SECRET,
      "AMS_CONFIGURATION_ENDPOINT" = var.AMS_CONFIGURATION_ENDPOINT,
      "DJANGO_SECRET_KEY" = var.DJANGO_SECRET_KEY,
      "KIBANA_BASE_URL" = var.KIBANA_BASE_URL,
      "LOGGING_LEVEL" = var.LOGGING_LEVEL,
      "REDIS_URI" = var.REDIS_URI,
      "JWT_KEY" = var.JWT_KEY,
      "SENDGRID_API_KEY" = var.SENDGRID_API_KEY,
    }

    service_binding {
      service_instance = cloudfoundry_service_instance.staticfiles.id
    }
    service_binding {
      service_instance = cloudfoundry_service_instance.datafiles.id
    }
    service_binding {
      service_instance = cloudfoundry_service_instance.database.id
    }
    service_binding {
      service_instance = cloudfoundry_service_instance.redis.tdp-redis-raft.id
    }
    service_binding {
      service_instance = cloudfoundry_service_instance.elasticsearch.id
    }
}

resource "cloudfoundry_network_policy" "backend_policy" {

  policy {
    destination_app = cloudfoundry_app.tdp-frontend-fake.id
    port            = "8080"
    protocol        = "tcp"
    source_app      = cloudfoundry_app.tdp-backend-fake.id
  }
  policy {
    destination_app = tdp-clamav-nginx-dev
    port            = "9000"
    protocol        = "tcp"
    source_app      = cloudfoundry_app.tdp-backend-fake.id
  }
}