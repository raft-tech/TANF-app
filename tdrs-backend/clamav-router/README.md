# CLAMAV 

In order to have one CLAMAV instance (existing in prod), the Nginx router 
for CLAMAV forwards the traffic from 'dev' and 'staging' spaces into
prod space, where the CLAMAV service exists.

## Deploy Nginx instance
To route the clamav traffic to clamav in prod, each space needs to have one instance of _Nginx Router_ which routes traffic to clamav.

In order to deploy the nginx router instance, change your directory to `tdrs-backend/clamav-router/` and run thefollowing command:

```
cf push {nginx_instance_name} -f manifest.yml
```
, where _nginx_instance_name_ can be : _tdp-clamav-nginx-test_. 

The instance name then will be set as an environment variable to redirect each instance traffic.

## Setup Individual Instances

First, set the environment variable __AV_SCAN_URL__ as follows:
```
Environment variable name: AV_SCAN_URL
Environment variable value: http://{nginx_instance_name}.apps.internal:9000/scan
```
To enable traffic between the "__nginx instance__" and "__clamav instance in production__", we need to add the network policiy and route between the two:

#### Add network policy from _{backend_instance}_ to _tdp-clamav-nginx_
```
cf add-network-policy {backend_instance} tdp-clamav-nginx --protocol tcp --port 9000
 ```
 where e.g: `backend_instance = tdp-backend-develop`

#### Add route from _{backend_instance}_ to _tdp-clamav-nginx_

 Note: Make sure to delete routes that are not being used. In some rare cases, a mal-assigned network policy can interfere with outgoing traffic. As an example, a policy like `cf delete-route app.cloud.gov --hostname tdp-frontend-staging`