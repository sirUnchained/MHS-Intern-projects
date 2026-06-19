import sqlite3
import contextlib
from configs.config import get_settings

settings = get_settings()


# For making a context safe program, I must make `connect_to_db` like this
@contextlib.contextmanager
def connect_to_db():
    """Connect to sqlite database."""
    conn = sqlite3.connect(settings.DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
