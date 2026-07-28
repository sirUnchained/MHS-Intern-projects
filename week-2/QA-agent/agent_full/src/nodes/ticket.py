from typing import Optional, Any
from sqlalchemy.orm import sessionmaker

from src.database.models import Ticket
from src.database.engine import get_engine
from src.state import UserTicketData, SupportState


def get_insert_ticket_node():
    # Create a session factory (reusable)
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)

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
            building_services=", ".join(new_ticket.get("services", [])),
        )

        # Insert into DB
        with SessionLocal() as session:
            session.add(new_ticket)
            session.commit()
            session.refresh(new_ticket)

        return {}

    return insert_ticket_node
