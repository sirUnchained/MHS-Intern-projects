from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from config import get_settings


# Create a SQLAlchemy engine (reusable)
def get_engine() -> Engine:
    """Return a SQLAlchemy engine connected to the pgvector-enabled PostgreSQL database."""

    settings = get_settings()

    engine = create_engine(url=settings.POSTGRESQL_DATABASE_LINK, echo=False)
    # Ensure pgvector extension is available
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    return engine


# Safe call for structured output
def safe_structured_invoke(structured_llm, messages, fallback, retries=1):
    for attempt in range(retries + 1):
        try:
            return structured_llm.invoke(messages)
        except Exception as e:
            if attempt == retries:
                print(f"[WARNING] structured_output failed, using fallback: {e}")
                return fallback
