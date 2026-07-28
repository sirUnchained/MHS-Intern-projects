from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import inspect
from typing import Optional, Any
from sqlalchemy.orm import sessionmaker

from src.helpers import get_engine
from src.state import UserTicketData, SupportState


def get_insert_ticket_node():
    # Create a session factory (reusable)
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
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
        building_services = Column(
            Text
        )  # store as comma-separated or JSON; here as string
        created_at = Column(DateTime, default=datetime.utcnow)

    # Create table if it dose not exists
    inspector = inspect(engine)
    if not inspector.has_table("tickets"):
        Base.metadata.create_all(engine)

    def insert_ticket_node(state: SupportState) -> dict[str, Any]:
        """
        LangGraph node that inserts a support ticket into the database.
        Expects state to contain:
        - user_id (str)
        - new_ticket (UserTicketData) – topic, budget, job, goals
        - building (BuildingInfo) – name, phone, services

        Returns updated state with ticket_id and a flag.
        """
        # Extract data from state
        user_id = state.get("user_id")
        new_ticket: Optional[UserTicketData] = state.get("new_ticket")

        # Validate required data
        if not user_id:
            raise ValueError("user_id is required to create a ticket.")
        if not new_ticket:
            raise ValueError("new_ticket is required to create a ticket.")

        # Prepare ticket record
        new_ticket = Ticket(
            user_id=user_id,
            topic=new_ticket.get("topic"),
            budget=new_ticket.get("budget"),
            job=new_ticket.get("job"),
            goals=new_ticket.get("goals"),
            building_name=new_ticket.get("building"),
            building_phone=new_ticket.get("phone"),
            building_services=new_ticket.get("services"),
        )

        # Insert into DB
        with SessionLocal() as session:
            session.add(new_ticket)
            session.commit()
            session.refresh(new_ticket)

        return {}

    return insert_ticket_node
