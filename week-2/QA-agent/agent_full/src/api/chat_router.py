from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status

from src.chat import chat_stream
from src.auth.security import decode_access_token

router = APIRouter(tags=["chat"])


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket, token: str = Query(...)):
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = payload["sub"]
    await websocket.accept()

    try:
        while True:
            user_message = await websocket.receive_text()
            async for chunk in chat_stream(q=user_message, user_id=user_id):
                await websocket.send_json(chunk)
            await websocket.send_json({"type": "done"})
    except WebSocketDisconnect:
        pass
