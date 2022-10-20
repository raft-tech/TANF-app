###
# Terraform settings and backend
###

terraform {
  required_providers {
    cloudfoundry = {
      source  = "cloudfoundry-community/cloudfoundry"
      version = "~>0.15"
    }
  }

  backend "s3" {
    # S3 region, bucket are specified in each <env>/backend.tfvars
    key    = "terraform.tfstate.dev"
    prefix = var.cf_app_name
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
  name     = var.cf_space_name
  org_name = var.cf_org_name
}

###
# Provision RDS instance
###

data "cloudfoundry_service" "rds" {
  name = "aws-rds"
}


resource "cloudfoundry_service_instance" "database" {
  name             = "tdp-db-dev"
  service_plan     = data.cloudfoundry_service.rds.service_plans["micro-psql"]
  space            = data.cloudfoundry_space.space.id
  recursive_delete = true
}

###
# Provision S3 buckets
###

data "cloudfoundry_service" "s3" {
  name = "s3"
}

resource "cloudfoundry_service_instance" "staticfiles" {
  name             = "tdp-staticfiles-dev"
  service_plan     = data.cloudfoundry_service.s3.service_plans["basic-public-sandbox"]
  space            = data.cloudfoundry_space.space.id
  recursive_delete = true
}

resource "cloudfoundry_service_instance" "datafiles" {
  name             = "tdp-datafiles-dev"
  space            = data.cloudfoundry_space.space.id
  service_plan     = data.cloudfoundry_service.s3.service_plans["basic-sandbox"]
  recursive_delete = true
}

data "cloudfoundry_app" "tdp_backend_raft" {
  name_or_id = var.cf_app_backend_raft_name
  space      = data.cloudfoundry_space.space.id
}
