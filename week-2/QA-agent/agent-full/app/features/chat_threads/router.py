import uuid
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Query,
    status,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import sessionmaker, Session

from agent.chat import chat_stream, get_graph
from app.core.security import decode_access_token
from app.core.engine import get_engine
from app.features.chat_threads.models import ChatThread
from app.features.chat_threads.schemas import ThreadCreate, ThreadOut
from app.deps import get_db, get_current_user
from app.features.auth.models import User
from app.features.chat_threads.models import ChatThread

import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


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
        logger.warning(
            "Attempt to get chats in an unknown thread with id: %s", thread_id
        )
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
        logger.warning("Attempt to delete an unknown thread with id: %s", thread_id)
        raise HTTPException(status_code=404, detail="Thread not found")

    graph = await get_graph()
    # deletes all checkpoints for this thread_id from the postgres saver
    await graph.checkpointer.adelete_thread(thread_id)

    db.delete(thread)
    db.commit()
    return {"status": "deleted", "thread_id": thread_id}


@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    token: str = Query(...),
    thread_id: str = Query(...),
):
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        logger.warning("Did not detect payload.")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = payload["sub"]

    # verify this thread actually belongs to the connecting user
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as db:
        print(payload)
        owns_thread = (
            db.query(ChatThread)
            .filter(ChatThread.thread_id == thread_id, ChatThread.user_id == user_id)
            .first()
        )
    if owns_thread is None:
        logger.warning("User %s attempt to get chats which is not for him.", user_id)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()

    try:
        logger.info("WS connected | thread_id=%s | user_id=%s", thread_id, user_id)
        while True:
            user_message = await websocket.receive_text()
            async for chunk in chat_stream(
                q=user_message, user_id=user_id, thread_id=thread_id
            ):
                await websocket.send_json(chunk)
            await websocket.send_json({"type": "done"})
    except WebSocketDisconnect:
        logger.info("WS disconnected | thread_id=%s", thread_id)
