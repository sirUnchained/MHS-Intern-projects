from fastapi import APIRouter, Depends, Query
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
