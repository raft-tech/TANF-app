# 19. Key Encryption Strategy

Date: 2022-09-14 (_updated 2022-09-14_)

## Status

Accepted

## Context

To keep up to date with security best practices, we want a way to store and retrieve sensitive values within our repository and CI/CD pipelines
as mentioned [in this issue](https://github.com/raft-tech/TANF-app/issues/1977). Two tools have been given proper weight to evaluate
[Mozilla SOPS](https://github.com/mozilla/sops#sops-secrets-operations) and a cloud managed [Vault instance](https://cloud.hashicorp.com/products/vault)

## Decision

The decision for this ADR is to continue forward with [SOPS](https://github.com/mozilla/sops#readme). SOPS is an editor of encrypted files that supports
YAML, JSON, ENV, INI and BINARY formats and encrypts with a(n) AWS KMS, GCP KMS, Azure Key Vault, age, or PGP key. These encrypted files can then be
safely stored as Data at Rest / Data in Transit. SOPS can be configured with a global file `.sops.yaml` stored at the root project directory that can
facilitate rules that govern how files are to be encrypted/decrypted.


### Consequences for using SOPS
- Will need a compatible key to encrypt/decrypt files. A AWS KMS key for each AWS account we push to, preferred over a PGP key that has to be "passed around" 
- Encrypted files will be stored on a open sourced public repository
- Ensure that files commited don't expose sensitive values. A combination of `trufflehog`, `gitsecrets` and possibly `git pre-commit hooks` to check/validate proper encoded ciphertext 

### Benefits for using SOPS
- Will have ownership over managed encrypted/decrypted files, won't have to rely on 3rd party solution to manage encryption to ciphertext
- Can manage different values for environment variables within a `.tfsecrets` file and encrypt/decrypt using SOPS within our pipeline
- Best case use is to use SOPS binary in a utility image in a CircleCI Executor
- VS Code has plugins available to automatically edit & encode/decode files directly as long as your key is available to use (~.aws has credentials configured) 

### Risks for using SOPS
- Terraform providers and CircleCI Orbs exist for SOPS, but might only be limited to decrypting files only
- Terraform providers and other developer contributed items could be out of date with security vulnerabilities
- Rotation of secret variables might have to be done manually using SOPS


### Consequences for using Vault
- Vault has many different types of abstracted layers of resources (KV engines, Auth methods and ACL policies), big learning curve to know which one to use and configure
- Some of the configuration options for Auth methods and ACL policies can only be accomplished through the API for CLI (not the UI)
- CircleCI at this time has [limited documentation](https://circleci.canny.io/cloud-feature-requests/p/integration-with-hashicorp-vault) to integrate with a managed Vault cluster. Other documentation refers to using the `kots` operator and CRD's but that is dependent on having CircleCI server setup on a K8s cluster that we have access to
- Vault, by default can be accessed through a admin token but will have to set up team auth methods and policies for both users and applications (CircleCI pipeline) its bad practice to utilize the admin account 100%
- In order for CircleCI to integrate with Vault, seperate Auth methods and ACL policies have to be set up in order to leverage the authentication and ID managment

### Benefits for using Vault


### Risks for using Vault


## Notes
-