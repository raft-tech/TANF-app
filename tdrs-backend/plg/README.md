# TDP PLG Stack
Before attempting to deploy the PLG stack or an postgres exporter you MUST have access to the production space in cloud.gov.

## Deploying PLG
Before deploying the PLG stack you must have the `ADMIN_EMAILS` and `DEV_EMAILS` variables defined in your shell environment. The variables should be a comma separated string of emails, eg: `ADMIN_EMAILS="email1@email.com, email2@email.com, email3@email.com"` and `DEV_EMAILS="email4@email.com, email5@email.com, email6@email.com"`.

Once both of the above items have been confirmed, you can target the production environment with the CF CLI and run the command below.

```
./deploy.sh -a -d tdp-db-prod
```

The command will deploy the entire PLG stack to the production environment and setup all appropriate network policies and routes.

## Deploying a Postgres Exporter
Before deploying a postgres exporter, you need to acquire the AWS RDS database URI for the RDS instance in the environment you are deploying the exporter to.

```
cf env <BACKEND_APP>
```

From the output of this command find the `VCAP_SERVICES` variable. Within this variable is a JSON list of services the app you provided is bound to. Find the `aws-rds` key and copy the `uri` value to your clipboard from the `credentials` key. Then you can deploy your exporter with the command below.

```
./deploy.sh -p <ENVIRONMENT_NAME> -d <RDS_SERVICE_NAME> -u <DATABASE_URI>
```
where `<ENVIRONMENT_NAME>` MUST be one of `[dev, staging, production]`, and `<DATABASE_URI>` is the uri you just copied from the app's `VCAP_SERVICES` environment variable. This command also handles all of the necessary networking configuration.

## DataFile reporting in Grafana

Use `data_files_datafile_view` for submission metadata with readable classifications. It exposes the DataFile columns, including `section_id`, plus `section` (the canonical Section name) and `program_type` (its Program code). All submission versions are included.

The view is generated and applied through the existing Grafana SQL pipeline. The database configuration step grants access to the `read_only`, `digit_sensitive`, and `admin_read_only` roles.

```sql
SELECT id, year, quarter, section, program_type, version
FROM data_files_datafile_view;
```

### Grafana Auth and RBAC Config
Grafana is accessible by any frontend app on a private route to users who have the correct role. The Grafana UI is not be accessible to any user or application unless they are routed to it via a frontend app. Grafana is configured to require user and password authentication. Having the extra layer of authentication is required because the roles defined in Grafana are not in alignment with the roles TDP defines. Assigning users to appropriate role and teams in Grafana allows for least privilege access to any information that Grafana might be able to display.

Grafana has three roles: `Admin`, `Editor`, and `Viewer`. We have also defined two teams (groups) in Grafana: `OFA` and `Raft` and several users. The teams are how we manage least privilege to Grafana's resources. Upon creation, all users are given one of the base roles. All Raft dev user accounts are given read only access (`Viewer`) to Grafana and OFA has a user account(s) associated with each of the roles. All users who are outside of OFA should always be assigned the `Viewer` role to maintain least privilege. All dashboards in Grafana are viewable by team as opposed to individual users/roles. Dashboard permissions are configured per dashboard and each team is given read only access to the appropriate dashboards. The `ofa-admin` user is the only direct user given access to resources. This account is given exclusive admin rights to all of Grafana.

All Grafana administration is handled under the `Administration` drop down in the hamburger menu which is only accessible to `Admin` users. Users can be created, assigned a role, and then associated with a team. As new dashboards are added to Grafana their permissions need to be configured for least privilege by going to Dashboards-><New Dashboard>->Settings->Permissions. The admin can use other dashboard permission configurations to help finish the configuration.

## Feedback report download metadata in Grafana

DIGIT users can query `public.reports_reportfile` through a PostgreSQL datasource in the **DIGIT** organization using the restricted database login `ofa_digit_sensitive`. This login inherits the `digit_sensitive` role, which receives SELECT access through [`scripts/apply-database-config.sh`](../../scripts/apply-database-config.sh) during database configuration. The grant does not add write privileges, extend the ordinary `read_only` role, or create a dashboard, panel, or database view.

`downloaded_at` records the first qualifying Data Analyst GET download for each report-file version, not the last download or a count of downloads. Repeated downloads preserve that timestamp; HEAD requests and downloads by DIGIT, OFA System Admin, or regional staff do not populate it. Tracking occurs before streaming completes, so it is not confirmation of completed delivery. A null timestamp means no qualifying download was recorded: older records were not backfilled, and tracking can fail without blocking delivery.

All report-file versions are available without an automatic latest-version or successful-upload filter. `COUNT(*)` counts report files, not downloads or distinct jurisdictions. The application's computed `downloaded_count` counts distinct non-null STTs with a recorded timestamp; `total_count` counts all distinct non-null STTs associated with that upload. Duplicate files for an STT are not separate jurisdiction downloads. `user_id` identifies the uploader, not the downloader.

In **Explore**, select the restricted PostgreSQL datasource and switch to **Code** to preview report metadata:

```sql
SELECT rf.id, rf.source_id, rf.stt_id, stt.name AS stt_name,
       region.name AS region_name, rf.year, rf.report_type,
       rf.version, rf.date_extracted_on, rf.downloaded_at
FROM public.reports_reportfile AS rf
LEFT JOIN public.stts_stt AS stt ON stt.id = rf.stt_id
LEFT JOIN public.stts_region AS region ON region.id = stt.region_id
ORDER BY rf.id DESC
LIMIT 100;
```

STT and region tables are already accessible to DIGIT. The LEFT JOINs retain report rows with missing STT or region metadata. `source_id` identifies the upload without requiring access to the ungranted `reports_reportsource` table.

### Verify read-only access

Run these checks using the same DIGIT datasource, not an admin datasource:

```sql
SELECT current_user AS database_user, current_database() AS database_name;

SELECT p.privilege,
       has_table_privilege(current_user, 'public.reports_reportfile', p.privilege) AS allowed
FROM (VALUES ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE'),
             ('TRUNCATE'), ('REFERENCES'), ('TRIGGER')) AS p(privilege);
```

Expect the database user to be `ofa_digit_sensitive`, connected to the intended application database, with SELECT allowed and all six other privileges denied. Verify the preview returns expected report metadata, including null timestamps; an empty table is valid but does not demonstrate visibility of populated rows. Do not test destructive statements against shared data. If unexpected privileges appear, ask an authorized database owner to investigate existing grants or role memberships rather than assuming this SELECT grant removes them.

For local verification, Grafana is available at `http://localhost:9400`. Compose startup does not apply the deployment role/user grants, and the checked-in datasource templates do not provision a PostgreSQL datasource. Provision the restricted role/login and a datasource with local credentials if needed; do not use production credentials or run the Cloud.gov deployment script locally. Shared-environment deployment or datasource changes require authorization.
