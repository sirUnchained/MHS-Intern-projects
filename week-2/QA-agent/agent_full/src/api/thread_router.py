import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.auth.deps import get_db, get_current_user
from src.auth.models import User
from src.database.models import ChatThread
from src.chat import get_graph

router = APIRouter(prefix="/chat", tags=["chat"])


class ThreadCreate(BaseModel):
    title: str | None = None


class ThreadOut(BaseModel):
    thread_id: str
    title: str | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/threads", response_model=ThreadOut)
def create_thread(
    payload: ThreadCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    thread = ChatThread(
        thread_id=str(uuid.uuid4()),
        user_id=user.username,
        title=payload.title or "New chat",
        created_at=datetime.now(timezone.utc),
    )
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return thread


@router.get("/threads", response_model=list[ThreadOut])
def list_threads(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(ChatThread)
        .filter(ChatThread.user_id == user.username)
        .order_by(ChatThread.created_at.desc())
        .all()
    )


@router.get("/threads/{thread_id}/messages")
async def get_thread_messages(
    thread_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    thread = (
        db.query(ChatThread)
        .filter(ChatThread.thread_id == thread_id, ChatThread.user_id == user.username)
        .first()
    )
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    graph = await get_graph()
    state = await graph.aget_state({"configurable": {"thread_id": thread_id}})
    messages = state.values.get("messages", []) if state else []

    return [
        {"id": m.id, "type": m.type, "content": getattr(m, "text", str(m.content))}
        for m in messages
    ]


@router.delete("/threads/{thread_id}")
async def delete_thread(
    thread_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    thread = (
        db.query(ChatThread)
        .filter(ChatThread.thread_id == thread_id, ChatThread.user_id == user.username)
        .first()
    )
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    graph = await get_graph()
    # deletes all checkpoints for this thread_id from the postgres saver
    await graph.checkpointer.adelete_thread(thread_id)

    db.delete(thread)
    db.commit()
    return {"status": "deleted", "thread_id": thread_id}
