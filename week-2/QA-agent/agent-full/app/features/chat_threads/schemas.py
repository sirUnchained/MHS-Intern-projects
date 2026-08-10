from pydantic import BaseModel

from datetime import datetime


class ThreadCreate(BaseModel):
    title: str | None = None


class ThreadOut(BaseModel):
    thread_id: str
    title: str | None
    created_at: datetime

    class Config:
        from_attributes = True
