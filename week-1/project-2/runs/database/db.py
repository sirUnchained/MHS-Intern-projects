import sqlite3
import contextlib
from configs.config import get_settings


@contextlib.contextmanager
def connect_to_db():
    """Connect to the SQLite database. Handles connection lifecycle automatically."""
    settings = get_settings()
    conn = sqlite3.connect(settings.DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
