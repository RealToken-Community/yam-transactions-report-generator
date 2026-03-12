from __future__ import annotations
import psycopg2
from psycopg2.extensions import connection as PGConnection

def get_pg_connection(pg_host, pg_port, pg_db, pg_user, pg_password) -> PGConnection:
    """
    Create and return a PostgreSQL connection.
    """
    return psycopg2.connect(
        host=pg_host,
        port=pg_port,
        dbname=pg_db,
        user=pg_user,
        password=pg_password,
        connect_timeout=10,
    )