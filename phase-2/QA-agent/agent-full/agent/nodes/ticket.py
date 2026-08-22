from typing import Optional, Any
from sqlalchemy.orm import sessionmaker

from app.features.tickets.models import Ticket
from app.core.engine import get_engine
from agent.state import UserTicketData, SupportState


def get_insert_ticket_node():
    # Create a session factory (reusable)
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)

    def insert_ticket_node(state: SupportState) -> dict[str, Any]:
        """
        Insert a support ticket into the database.

        Extracts ticket data from the conversation state and persists it.
        The node expects the state to contain user_id and new_ticket fields
        with all required ticket information.

        Args:
            state (SupportState): Conversation state containing:
                - user_id (str): User identifier
                - new_ticket (UserTicketData): Ticket details including topic,
                  budget, job description, and goals

        Returns:
            dict[str, Any]: Updated state containing:
                - ticket_id: The newly created ticket's ID
                - flag: Status flag indicating success/failure

        Raises:
            ValueError: If user_id or new_ticket is missing from the state.
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
