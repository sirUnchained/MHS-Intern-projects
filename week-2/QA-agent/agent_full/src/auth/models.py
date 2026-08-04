import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum

from src.database.base import Base
from src.database.engine import get_engine


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def migrate():
    """Create the users table if it doesn't exist yet."""
    engine = get_engine()
    Base.metadata.create_all(engine)
