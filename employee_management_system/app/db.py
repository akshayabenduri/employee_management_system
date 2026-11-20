"""Database helper: one place to connect to MySQL and run queries."""
import mysql.connector
from config import Config


def get_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
    )


def run_query(sql, params=None, fetch="all", commit=False):
    """
    Run one SQL query safely using parameters (prevents SQL injection).
    fetch: "all" -> list of rows, "one" -> single row, None -> no fetch
    commit: True for INSERT / UPDATE / DELETE
    Returns rows, or number of affected rows when fetch is None.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        if commit:
            conn.commit()
        if fetch == "all":
            return cursor.fetchall()
        if fetch == "one":
            return cursor.fetchone()
        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()
