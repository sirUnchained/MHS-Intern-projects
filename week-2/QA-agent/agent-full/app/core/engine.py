from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


from app.core.config import get_settings

_engine: Engine | None = None


# This pattern is singleton?
def get_engine() -> Engine:
    """
    Get or create the SQLAlchemy database engine singleton.

    Initializes the engine on first call and ensures the pgvector extension
    is enabled in the database.

    Returns:
        Engine: Configured SQLAlchemy engine instance.

    Note:
        The engine is cached globally, subsequent calls return the same instance.
        The pgvector extension is created automatically if it doesn't exist.
    """

    global _engine
    if _engine is not None:
        return _engine

    settings = get_settings()
    _engine = create_engine(url=settings.POSTGRESQL_DATABASE_LINK, echo=False)
    with _engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    return _engine
