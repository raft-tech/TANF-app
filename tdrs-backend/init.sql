CREATE ROLE readaccess;
GRANT CONNECT ON DATABASE tdrs_test TO readaccess;
GRANT USAGE ON SCHEMA public TO readaccess;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readaccess;
CREATE USER read_grafana_user WITH PASSWORD '12345abc';
GRANT readaccess TO read_grafana_user;