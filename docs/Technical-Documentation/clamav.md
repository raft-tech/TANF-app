# ClamAV connection
We are reducing the number of ClamAV servers and just hitting the one in the prod space.
This is to increase resources available in lower environments.

Before connections to the single ClamAV server can be made, a network policy needs to be created.

Add network policy to allow conection to prod clamAV to access backend
`cf add-network-policy "$CGAPPNAME_BACKEND" clamav-rest -s tanf-prod --protocol tcp --port 9000`