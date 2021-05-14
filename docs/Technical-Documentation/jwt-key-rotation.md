# Rotating JWT Keys

## Context

To maintain good security, we will periodically rotate the JWT keys used to control authentication and authorization to our application. This document outlines the process of how to do this.

**Warning** Production sites will need to be taken down for maintenance when rotating keys, as the rotation will automatically invalidate all current sessions.

### 1. Generate New Keys

In your Mac terminal (or bash terminal in Windows), enter the following command:
```bash=
openssl req -nodes -x509 -days 90 -newkey rsa:2048 -keyout jwtRS256prv.pem -out jwtRS256pub.crt
```

You will receive the following response. Answering questions when prompted is not necessary.

```bash
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:
State or Province Name (full name) [Some-State]:
Locality Name (eg, city) []:
Organization Name (eg, company) [Internet Widgits Pty Ltd]:
Organizational Unit Name (eg, section) []:
Common Name (e.g. server FQDN or YOUR name) []:
Email Address []:
```

You can now check the contents of your keys with these commands
```bash=
cat jwtRS256prv.pem
# returns private key
cat jwtRS256pub.crt
# returns public key
```

### 2. Base64 Encode Private Key

We use Base64 Encoded Private Keys to make it easier to save to cloud environments and local `.env` files.

```bash
openssl enc -base64 -in jwtRS256prv.pem -out jwtRS256prv.pem.base64

cat jwtRS256prv.pem.base64
```

NOTE: Linux users must disable line wrapping by adding the argument `-w 0` to get a properly formatted one-line value.
```bash
openssl enc -base64 -w 0 -in jwtRS256prv.pem -out jwtRS256prv.pem.base64
cat jwtRS256prv.pem.base64
```

### 3. Copy Keys

#### Dev/Staging Environments
1. Distribute the private key to development staff securely to copy to `.env` files as the value for key `JWT_KEY`
2. Update the environment variable `JWT_KEY` with the private key in cloud.gov backend development and staging environments
3. Login to the [Login.gov Sandbox](https://dashboard.int.identitysandbox.gov/) and update the public key there

Note: Login.gov requires the key to be uploaded in PEM format, which is the format we produced in the `jwtRS256pub.crt` file.

![pem_upload](https://user-images.githubusercontent.com/1181427/114887693-ae6eef00-9dd6-11eb-98cc-2de3f061337a.png)

#### CI/CD Environment
**Note** _Please generate a separate set of keys for the CI/CD environment_
1. Distribute the private key to development staff securely to copy to `.env` files as the value for key `JWT_CERT_TEST`
2. Update the variable `JWT_KEY_TEST` in CircleCI with the new public key.

#### Production Environment
**Note** _Please generate a separate set of keys for the Production environment_

Production environment key distribution will be handled by Government authorized personnel with Government computers and PIV access.
1. Copy the private key to cloud.gov backend environment variable `JWT_KEY`
2. Copy the public key to the login.gov production environment

**Note** 
- We will need to update this document with the link to login to the login.gov production environment setup when we have access to it.
- More information on `openssl` can be found at [openssl.org](https://www.openssl.org/docs/manmaster/man1/openssl.html)
