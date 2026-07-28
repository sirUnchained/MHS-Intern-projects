from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Integer, Text, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

from src.database.engine import get_engine

Base = declarative_base()


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


def migrate():
    """Create all tables that don't exist yet."""
    engine = get_engine()
    inspector = inspect(engine)
    if not inspector.has_table("tickets"):
        Base.metadata.create_all(engine)
