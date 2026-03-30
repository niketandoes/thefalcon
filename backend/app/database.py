# app/database.py
import os
import psycopg2
import psycopg2.extras  # for RealDictCursor (rows as dicts, not tuples)
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# --- Connection config built from environment variables ---
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 5432)),
    "dbname":   os.getenv("DB_NAME", "split_it_fair"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}


def get_connection():
    """
    Open and return a raw psycopg2 connection.
    Caller is responsible for closing it.
    Prefer the get_cursor() context manager below for everyday use.
    """
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return psycopg2.connect(**DB_CONFIG)


@contextmanager
def get_cursor(commit: bool = True):
    """
    Context manager that yields a dict-cursor, then auto-commits (or rolls
    back on error) and closes the connection.

    Usage:
        with get_cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()   # returns {'id': ..., 'email': ..., ...}

    Args:
        commit: Set to False for read-only queries (skips the commit call).
    """
    conn = get_connection()
    try:
        # RealDictCursor returns rows as dicts instead of plain tuples
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            yield cur
            if commit:
                conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def check_connection() -> bool:
    """Quick health-check — returns True if the DB is reachable."""
    try:
        with get_cursor(commit=False) as cur:
            cur.execute("SELECT 1")
        return True
    except psycopg2.OperationalError as e:
        print(f"[DB] Connection failed: {e}")
        return False
