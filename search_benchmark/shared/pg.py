import psycopg2

from psycopg2 import pool, connect
import os
from search_benchmark.shared.config import get_pg_db_name, get_pg_user, get_pg_password, get_pg_host, get_pg_port

def get_db_connection():
    """
    Creates and returns a new database connection using environment variables.
    """
    db_name = get_pg_db_name()
    user = get_pg_user()
    password = get_pg_password()
    host = get_pg_host()
    port = get_pg_port()
    return psycopg2.connect(dbname=db_name, user=user, password=password, host=host, port=port)

def put_db_connection(connection):
    if connection:
        connection.close()