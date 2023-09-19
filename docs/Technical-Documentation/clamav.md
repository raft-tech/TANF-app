# ClamAV connection
We are reducing the number of ClamAV servers and just hitting the one in the prod space.
This is to increase resources available in lower environments.

We use a single NGINX server per space to route each app in that space to the ClamAV server in the production space. 

[Here is more detailed documentation](../../tdrs-backend/clamav-router/README.md) for how we are implementing this.