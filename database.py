import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import psycopg
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))


def get_connection():
    """Open a PostgreSQL connection using DATABASE_URL or DB_* settings."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg.connect(database_url)
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


@contextmanager
def database_cursor() -> Iterator[Any]:
    """Yield a cursor and close both cursor and connection after the query."""
    connection = get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                yield cursor
    finally:
        connection.close()


def run_query(query: str, parameters: tuple = (), fetch: bool = False):
    """Execute one SQL query and optionally return all result rows."""
    with database_cursor() as cursor:
        cursor.execute(query, parameters)
        return cursor.fetchall() if fetch else None
