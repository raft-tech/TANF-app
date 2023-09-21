# How to DROP existing DB and Recreate a fresh DB

### Connecting to DB service
First step is to connect to the instance DB (see [this](CloudFoundry-DB-Connection.md)). 

e.g: `cf connect-to-service tdp-backend-qasp tdp-db-dev`

After connection to the DB is made (the step above will make a psql connection), then the following Postgres commands have to run:

1. List the DBs: `\l`
2. find the associated DB name with instance. E.g: `tdp_db_dev_qasp`
3. use the following command to delete the DB: `DROP DATABASE {DB_NAME}`
4. use the following command to create the DB: `CREATE DATABASE {DB_NAME}`

After the DB is created, since the database is cinoketely empty, we will need to redeploy the app again to create tables (or alternatively we can restore a good backup), and then we should run populate stt command to add STT data to the empty DB

`./manage.py populatestts`
