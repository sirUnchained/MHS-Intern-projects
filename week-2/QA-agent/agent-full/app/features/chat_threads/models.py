from sqlalchemy import Column, String, DateTime, Integer
from datetime import datetime, timezone

from db.base import Base
from app.core.engine import get_engine


class ChatThread(Base):
    __tablename__ = "chat_threads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def migrate():
    """Create the chat_threads table if it doesn't exist yet."""
    engine = get_engine()
    Base.metadata.create_all(engine)
