"""Create a read-only user for the PLG database."""

from django.db import connection
from django.conf import settings

def run(*args):
    """Create a read-only user for the PLG database."""
    # ./manage.py runscript create_readonly_grafana_user --script-args "test" "test2"
    GRAFANA_PASSWORD = args[0]
    GRAFANA_USER = args[1]
    if not GRAFANA_PASSWORD or not GRAFANA_USER:
        print("Grafana user and password must be provided.")
        return
    
    OFA_USER = args[2] if len(args) > 2 else None
    OFA_PASSWORD = args[3] if len(args) > 3 else None

    OFA_ADMIN_USER = args[4] if len(args) > 4 else None
    OFA_ADMIN_PASSWORD = args[5] if len(args) > 5 else None

    print("Creating Grafana user...")

    DB_NAME = settings.DATABASES['default']['NAME']
    print("Creating Grafana user...")
    if not GRAFANA_PASSWORD or not GRAFANA_USER:
        print("Grafana user and password must be provided.")
        return

    with open("init.sql", "r") as file:
        print("Reading init.sql file...")
        while True:
            sql_query = file.readline()
            if not sql_query:
                break
            if "$GRAFANA_USER" in sql_query:
                sql_query = sql_query.replace("$GRAFANA_USER", GRAFANA_USER)
            if "$GRAFANA_PASSWORD" in sql_query:
                sql_query = sql_query.replace("$GRAFANA_PASSWORD", GRAFANA_PASSWORD)
            if "$DB_NAME" in sql_query:
                sql_query = sql_query.replace("$DB_NAME", DB_NAME)

            if "$OFA_USER" in sql_query and OFA_USER:
                sql_query = sql_query.replace("$OFA_USER", OFA_USER)
            elif "$OFA_USER" in sql_query and not OFA_USER:
                continue
            if "$OFA_PASSWORD" in sql_query and OFA_PASSWORD:
                sql_query = sql_query.replace("$OFA_PASSWORD", OFA_PASSWORD)
            elif "$OFA_PASSWORD" in sql_query and not OFA_PASSWORD:
                continue
            if "$OFA_ADMIN_USER" in sql_query and OFA_ADMIN_USER:
                sql_query = sql_query.replace("$OFA_ADMIN_USER", OFA_ADMIN_USER)
            elif "$OFA_ADMIN_USER" in sql_query and not OFA_ADMIN_USER:
                continue
            if "$OFA_ADMIN_PASSWORD" in sql_query and OFA_ADMIN_PASSWORD:
                sql_query = sql_query.replace("$OFA_ADMIN_PASSWORD", OFA_ADMIN_PASSWORD)
            elif "$OFA_ADMIN_PASSWORD" in sql_query and not OFA_ADMIN_PASSWORD:
                continue
            print(f"--Executing SQL query: {sql_query.strip()}")
            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)
            except Exception as e:
                if "already exists" in str(e):
                    pass
                else:
                    print(f"An error occurred: {e}")
                    print("An unexpected error occurred.")
                continue
        return
    print("Grafana readonly user created successfully.")
