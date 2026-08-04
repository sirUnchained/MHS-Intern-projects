from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy.orm import sessionmaker

from src.chat import chat_stream
from src.auth.security import decode_access_token
from src.database.engine import get_engine
from src.database.models import ChatThread

router = APIRouter(tags=["chat"])


@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    token: str = Query(...),
    thread_id: str = Query(...),
):
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = payload["sub"]

    # verify this thread actually belongs to the connecting user
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as db:
        owns_thread = (
            db.query(ChatThread)
            .filter(ChatThread.thread_id == thread_id, ChatThread.user_id == user_id)
            .first()
        )
    if owns_thread is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()

    try:
        while True:
            user_message = await websocket.receive_text()
            async for chunk in chat_stream(
                q=user_message, user_id=user_id, thread_id=thread_id
            ):
                await websocket.send_json(chunk)
            await websocket.send_json({"type": "done"})
    except WebSocketDisconnect:
        pass
