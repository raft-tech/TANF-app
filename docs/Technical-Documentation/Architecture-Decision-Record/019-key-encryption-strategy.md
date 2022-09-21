# 19. Key Encryption Strategy

Date: 2022-09-14 (_updated 2022-09-14_)

## Status

Accepted

## Context

To keep up to date with security best practices, we want a way to store and retrieve sensitive values within our repository
and CI/CD pipelines as mentioned [in this issue](https://github.com/raft-tech/TANF-app/issues/1977). Two tools have been
given proper weight to evaluate [Mozilla SOPS](https://github.com/mozilla/sops#sops-secrets-operations) and a cloud managed [Vault instance](https://cloud.hashicorp.com/products/vault)

## Decision

The decision for this ADR is to continue forward with [SOPS](https://github.com/mozilla/sops#readme). SOPS is an editor
of encrypted files that supports YAML, JSON, ENV, INI and BINARY formats and encrypts with a(n) AWS KMS, GCP KMS,
Azure Key Vault, age, or PGP key. These encrypted files can then be stored as Data at Rest / Data in Transit.
SOPS can be configured with a global file `.sops.yaml` stored at the root project directory that can facilitate rules
that govern how files are to be encrypted/decrypted.


### Consequences for using SOPS
- Will need a compatible key to encrypt/decrypt files. A AWS KMS key for each AWS account we push to is preferred over
  a PGP/Age key that has to be "passed around"
- Encrypted files will be stored on a open sourced public repository
- Ensure that files commited don't expose sensitive values. A combination of `trufflehog`, `gitsecrets` and
  possibly `git pre-commit hooks` to check/validate proper encoded files/ciphertext

### Benefits for using SOPS
- Will have ownership over managed encrypted/decrypted files, won't have to rely on 3rd party solution to manage
  encryption of secrets
- Can manage different values for environment variables within a `.tfsecrets` file and encrypt/decrypt using
  SOPS within our pipeline
- Best case use is to use SOPS binary in a utility image in a CircleCI Executor
- VS Code has plugins available to automatically edit & encode/decode files directly as long as your key is available
  to use (~/.aws has correct credentials configured)
- Can be no cost depending on the key being used to encrypt/decrypt; there is a cost to using provisioned AWS KMS keys
- Better for dealing with single application use with fewer secrets to be managed

### Risks for using SOPS
- Terraform providers and CircleCI Orbs exist for SOPS, but might only be limited to decrypting files only
- Terraform providers and other developer contributed items could be out of date with security vulnerabilities
- Rotation of secret variables might have to be done manually using SOPS

### Consequences for using Vault
- Vault has different types of abstracted layers of resources (KV engines, Auth methods and ACL policies); will have to
  tackle learning curve to learn many of the features and setups required for optimized secure clusters
- Some configuration options for Auth methods and ACL policies can only be accomplished through the API or CLI (not the UI)
- CircleCI at this time has [limited documentation](https://circleci.canny.io/cloud-feature-requests/p/integration-with-hashicorp-vault) to integrate with a managed Vault cluster.
  Other documentation refers to using the `kots` operator and CRD's but that is dependent on having CircleCI server setup on a K8s cluster
- Vault, by default can be accessed through a admin token but will have to set up with team auth methods and policies for both
  users and applications (CircleCI pipeline); its bad practice to utilize the admin account 100%
- One of the features of vault is that it can be 'sealed' in the case of credentials being compromised, the unseal process involves provided shamir keys to 'unlock' access.
  These shamir keys aren't created by default when working with a managed vault cloud, but are created when setting up a self-hosted vault cluster
- By default, the token that can be used for admin login (with the managed Vault HA Cluster) is only good for a certain amount of time; creation of new token
  is automatic upon TTL expiration of the old token
- Cost will be a factor depending on tier selected for managed HA Vault Cluster

### Benefits for using Vault
- Customized `Key-Value` engine for storing secrets that can be managed with RBAC
- Integrated with use of CircleCI pipeline Auth method to retrieve said secrets in vault
- Short-lived dynamic provisioning of secrets/tokens can be accomplished through extra setup of auth roles
- Won't have to worry about setting up validation prior to commiting possible exposed (clear text) secrets
- Better for dealing with many secrets spread across/integrated with many services

### Risks for using Vault
- If (in the rare case) AWS region that hosts Vault managed clusters goes down, vault will automatically seal. Since separate
  key shards weren't provide upon given vault cluster creation; options to 'unseal' or 'unlock' the service isn't known upon AWS regions
  being back on-line
- Recommended setup for production Vault HA cluster is with a private IP in the Vault Cloud Console, Peering then can be accomplished through AWS managed VPC's to connect to
  the managed Vault Cluster. This is to address attack vector's and lessen the attack plane
- No way to connect to private IP without access to AWS resources (EC2, VPC peering)
- In order for CircleCI to integrate with Vault, separate Auth methods, Roles and ACL policies have to be set up in order to
  leverage the restricted authentication that would be required of the least privilege access model


## Notes
-