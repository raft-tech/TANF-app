from django.db import connection

def run(*args):
    """This script creates a read-only user for the PLG database."""
    GRAFANA_PASSWORD = args[0]
    GRAFANA_USER = args[1]
    with open("init.sql", "r") as file:
        while True:
            sql_query = file.readline()
            if not sql_query:
                break
            if "$GRAFANA_USER" in sql_query:
                sql_query = sql_query.replace("$GRAFANA_USER", GRAFANA_USER)
            if "$GRAFANA_PASSWORD" in sql_query:
                sql_query = sql_query.replace("$GRAFANA_PASSWORD", GRAFANA_PASSWORD)
            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)
            except Exception as e:
                print(f"Error executing SQL query: {sql_query}")
                print(f"Exception: {e}")
                continue
    