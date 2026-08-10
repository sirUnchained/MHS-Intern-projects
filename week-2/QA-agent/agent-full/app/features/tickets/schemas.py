from pydantic import BaseModel
from datetime import datetime


class TicketOut(BaseModel):
    id: int
    user_id: str
    topic: str | None
    budget: str | None
    job: str | None
    goals: str | None
    building_name: str | None
    building_phone: str | None
    building_services: str | None
    created_at: datetime

    class Config:
        from_attributes = True
