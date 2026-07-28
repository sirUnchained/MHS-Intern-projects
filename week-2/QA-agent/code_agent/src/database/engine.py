from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


from config import get_settings

_engine: Engine | None = None


# This pattern is singleton?
def get_engine() -> Engine:
    global _engine
    if _engine is not None:
        return _engine

    settings = get_settings()
    _engine = create_engine(url=settings.POSTGRESQL_DATABASE_LINK, echo=False)
    with _engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    return _engine
