from sqlalchemy import Column, String, DateTime, Integer, Text
from datetime import datetime, timezone

from db.base import Base
from app.core.engine import get_engine


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
    """Create the tickets table if it doesn't exist yet."""
    engine = get_engine()
    Base.metadata.create_all(engine)
