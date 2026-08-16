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
    """
    Stream chat responses from the LangGraph agent as structured events.

    This async generator consumes messages from a conversational agent graph,
    filtering for relevant nodes and yielding structured chunks suitable for
    WebSocket forwarding to a frontend client.

    Args:
        q (str): The user's input message/question to process.
        user_id (str): Unique identifier for the user, used to maintain
            conversation context and user-specific state.
        thread_id (str): Thread identifier that groups messages into a
            conversation session. The agent uses this to maintain history
            and provide coherent responses.

    Yields:
        dict: A structured chunk with one of two formats:

        1. Tool call event:
        ```python
            {
                "type": "tool_call",
                "name": str,      # Name of the tool being invoked
                "args": dict      # Arguments passed to the tool
            }
        ```

        2. Text token event:
        ```python
            {
                "type": "token",
                "content": str,   # A piece of the assistant's response text
                "message_id": str # ID to enable feedback (like/dislike) via
                                  # POST /chat/feedback
            }
        ```

    Notes:
        - Only processes messages from three specific nodes:
          main_agent_node, insert_ticket_node, building_classifier_and_ticket_node
    """

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
            yield {
                "type": "token",
                "content": msg_chunk.text,
                "message_id": msg_chunk.id,
            }
