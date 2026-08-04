from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, sessionmaker
from typing import Optional

from src.auth.deps import get_db, require_admin
from src.auth.models import User
from src.database.models import Ticket
from src.database.schemas import TicketOut

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/tickets", response_model=list[TicketOut])
def get_tickets(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
    skip: int = 0,
    limit: int = 50,
    user_id: Optional[str] = Query(None),
):
    query = db.query(Ticket)
    if user_id:
        query = query.filter(Ticket.user_id == user_id)
    return query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/tickets/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
    user_id: Optional[str] = Query(None),
):
    # First, find the ticket
    query = db.query(Ticket).filter(Ticket.id == ticket_id)

    # If user_id is provided, verify the ticket belongs to that user
    if user_id:
        query = query.filter(Ticket.user_id == user_id)

    ticket = query.first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Delete the ticket
    db.delete(ticket)
    db.commit()

    return {"message": f"Ticket {ticket_id} deleted successfully"}
