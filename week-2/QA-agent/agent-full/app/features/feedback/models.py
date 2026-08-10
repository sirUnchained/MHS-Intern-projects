from sqlalchemy import Column, String, DateTime, Integer, Text, SmallInteger, inspect
from datetime import datetime, timezone

from db.base import Base
from app.core.engine import get_engine


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    thread_id = Column(String, nullable=False, index=True)
    message_id = Column(String, nullable=False, index=True)
    rating = Column(SmallInteger, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def migrate():
    """Create the feed_backs table if it doesn't exist yet."""
    engine = get_engine()
    Base.metadata.create_all(engine)
