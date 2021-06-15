# Terraform

These docs are verbose because this is technology with which developers will rarely interact. I suggest you settle in for a nice long read with your favorite drink of choice.

## Prior Art

### Persistent vs Ephemeral Infrastructure
Adapted from: <https://github.com/HHS/Head-Start-TTADP#persistent-vs-ephemeral-infrastructure>

**The infrastructure used to run this application can be categorized into two distinct types: _ephemeral_ and _persistent_**

* **Ephemeral infrastructure** is all the infrastructure that is recreated each time the application deploys. Ephemeral infrastructure includes the "application(s)" (as defined in Cloud.gov), the EC2 instances the application runs on, and the routes that application utilizes. Our CircleCI configuration describes this infrastructure and deploys it to Cloud.gov.
* **Persistent infrastructure** is all the infrastructure that remains constant and unchanged despite application deployments. Persistent infrastructure includes the database used in each development environment. Our Terraform configuration files describe this infrastructure and instantiates it on Cloud.gov.

> This concept is often referred to as _mutable_ vs _immutable_ infrastructure.

### Infrastructure as Code

A high-level configuration syntax, called [Terraform language][language], describes our infrastructure. This allows a blueprint of our system to be versioned and treated as we do any other code. This configuration can be acted on locally by a developer if deployments need to be created manually, but it is mostly and ideally executed by CirclCI.

###  Terraform workflow

Terraform integrates into our CircleCI pipeline via the [Terraform orb][orb], and is formally described in our `deploy-infrastructure` CircleCI job. Upon validating its configuration, Terraform reads the current state of any already-existing remote objects to make sure that the Terraform state is up-to-date, and compares the current configuration to the prior state, noting all differences. Terraform creates a "plan" and proposes a set of change actions that should, if applied, make the remote objects match the configuration – this is the essence of _infrastructure as code_.

### Terraform state

We use an S3 bucket created by Cloud Foundry in Cloud.gov as our remote backend for Terraform. This backend maintains the "state" of Terraform and makes it possible for us to make automated deployments based on changes to the Terraform configuration files. **This is the only part of our infrastructure that must be manually configured.**

## Local Set Up For Manual Deployments

Sometimes a developer will need to run Terraform locally to perform manual operations. Perhaps a new TF State S3 bucket needs to be created in another environment, or there are new services or other major configuration changes that need to be tested first.

1. **Install terraform**

    - On macOS: `brew install terraform`
    - On other platforms: [Download and install terraform][tf]

1. **Install Cloud Foundry CLI tool**

    - On macOS: `brew install cloudfoundry/tap/cf-cli`
    - On other platforms: [Download and install cf][cf-install]

1. **Login to Cloud Foundry**
    ```bash
       # login
       cf login -a api.fr.cloud.gov --sso
       # Follow temporary authorization code prompt.
       
       # Select the target org (probably hhs-acf-prototyping), 
       # and the space within which you want to build infrastructure.
       
       # Spaces:
       # dev = tanf-dev
       # staging = tanf-staging
       # prod = tanf-prod
   ```

1. **Set up Terraform environment variables**

   In the `/terraform` directory, you can run the `create_tf_vars.sh` script which can be modified with details of your current environment, and will yield a `variables.tfvars` file which must be later passed in to Terraform. For more on this, check out [terraform variable definitions][tf-vars].

   ```bash
   ./create_tf_vars.sh
   
   # Should generate a file `variables.tfvars` in the current directory.
   # Your file should look something like this:
   #
   # env = "dev"
   # cf_user = "some-dev-user"
   # cf_password = "some-dev-password"
   # cf_space_name = "tanf-dev"
   #
   ```
### Terraform State S3 Bucket

The service key details provide you with the credentials that are used with common file transfer programs by humans or configured in external systems. Typically, you would create a unique service key for each external client of the bucket to make it easy to rotate credentials in case they are leaked.

1. **Create S3 Bucket for Terraform State**

   ```bash
    cf create-service s3 basic-sandbox tdp-tf-states
   ```

1. **Create service key**

   ```bash
   cf create-service-key tdp-tf-states tdp-tf-key
   ```

   > To later revoke access (e.g. when no longer required, or when compromised), you can run `cf delete-service-key tdp-tf-states tdp-tf-key`.

1. **Get the credentials from the service key**
   ```bash
   cf service-key tdp-tf-states tdp-tf-key
   ```
   > **Rotating credentials:**
   > 
   > The S3 service creates unique IAM credentials for each application binding or service key. To rotate credentials associated with an application binding, unbind and rebind the service instance to the application. To rotate credentials associated with a service key, delete and recreate the service key.
   

<!-- Links -->

[aws-config]: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-config
[aws-install]: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html
[cloudgov-bind]: https://cloud.gov/docs/deployment/managed-services/#bind-the-service-instance
[cloudgov-deployer]: https://cloud.gov/docs/services/cloud-gov-service-account/
[cloudgov-service-keys]: https://cloud.gov/docs/services/s3/#interacting-with-your-s3-bucket-from-outside-cloudgov
[cf-install]: https://docs.cloudfoundry.org/cf-cli/install-go-cli.html
[tf]: https://www.terraform.io/downloads.html
[tf-vars]: https://www.terraform.io/docs/configuration/variables.html#variable-definitions-tfvars-files
[orb]: https://circleci.com/developer/orbs/orb/circleci/terraform
[language]: https://www.terraform.io/docs/language/index.html