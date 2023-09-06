## CLAMAV 

In order to have one CLAMAV instance (existing in prod), the Nginx router 
for CLAMAV forwards the traffic from 'dev' and 'staging' spaces into
prod space, where the CLAMAV service exists.

## Deploy Nginx instance
In order to deploy the nginx router instance, change your directory to `tdrs-backend/clamav-router/` and run thefollowing command:

```
cf push {nginx_instance_name} -f manifest.yml
```
, where _nginx_instance_name_ can be : _tdp-clamav-nginx-test_. 

The instance name then will be set as an environment variable to redirect each instance traffic.

Set the environment variable __AC_SCAN_URL__ as follows:
```
Environment variable name: AV_SCAN_URL
Environment variable value: http://{nginx_instance_name}.apps.internal:9000/scan
```
To enable traffic between the "__nginx instance__" and "__clamav instance in production__", we need to add the network policiy between the two:

```
cf add-network-policy tdp-backend-develop tdp-clamav-nginx --protocol tcp --port 9000
 ```

 Note: Make sure to delete network-polcies that are not being used. In some rare cases, a mal-assigned network policy can interfere with outgoing traffic.