import sqlite3
import contextlib
from configs.config import get_settings

settings = get_settings()


# This function handles the complete lifecycle of a database connection.
# By using the 'with' statement, callers can execute queries safely without
# worrying about manually closing the connection, even if an exception occurs.
@contextlib.contextmanager
def connect_to_db():
    """Connect to sqlite database."""
    conn = sqlite3.connect(settings.DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
