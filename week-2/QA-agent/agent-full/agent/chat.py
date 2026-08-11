from langchain_core.messages import HumanMessage
from agent.graph import build_graph
from app.core.config import get_settings
import os

_graph = None


async def get_graph():
    """Get the graph! Note that this is an async function"""
    global _graph
    if _graph is None:
        _graph = await build_graph()
    return _graph


async def chat_stream(q: str, user_id: str, thread_id: str):
    """Async generator yielding structured chunks for a websocket to forward."""

    graph = await get_graph()
    config = {"configurable": {"thread_id": thread_id}}

    async for msg_chunk, metadata in graph.astream(
        input={"messages": [HumanMessage(content=q)], "user_id": user_id},
        config=config,
        stream_mode="messages",
    ):
        node = metadata.get("langgraph_node")
        if node not in (
            "main_agent_node",
            "insert_ticket_node",
            "building_classifier_and_ticket_node",
        ):
            continue

        if msg_chunk.tool_calls:
            for tc in msg_chunk.tool_calls:
                yield {
                    "type": "tool_call",
                    "name": tc.get("name"),
                    "args": tc.get("args"),
                }
        elif msg_chunk.text:
            # message_id lets the frontend attach a like/dislike to this
            # specific assistant message later via POST /chat/feedback.
            yield {
                "type": "token",
                "content": msg_chunk.text,
                "message_id": msg_chunk.id,
            }
