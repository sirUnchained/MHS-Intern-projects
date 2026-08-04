from sqlalchemy import Column, String, DateTime, Integer, Text, SmallInteger, inspect
from datetime import datetime, timezone

from src.database.base import Base
from src.database.engine import get_engine


class ChatThread(Base):
    __tablename__ = "chat_threads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    topic = Column(String)
    budget = Column(String)
    job = Column(String)
    goals = Column(Text)
    building_name = Column(String)
    building_phone = Column(String)
    building_services = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


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
    """Create all tables that don't exist yet (users, tickets, feedback, chat_threads)."""
    engine = get_engine()
    inspector = inspect(engine)
    required_tables = ("users", "tickets", "feedback", "chat_threads")
    if any(not inspector.has_table(t) for t in required_tables):
        Base.metadata.create_all(engine)
