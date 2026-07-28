from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage

from src.graph import build_graph
from config import get_settings


def chat(q: str, user_id: str):
    graph = build_graph()
    settings = get_settings()
    config: RunnableConfig = {"configurable": {"thread_id": user_id}}

    for msg_chunk, metadata in graph.stream(
        input={"messages": [HumanMessage(content=q)], "user_id": user_id},
        config=config,
        stream_mode="messages",
    ):
        node = metadata.get("langgraph_node")

        if node == "main_agent_node" or node == "insert_ticket_node":
            if settings.IS_DEVELOPMENT:
                if msg_chunk.tool_calls:
                    for tc in msg_chunk.tool_calls:
                        print(
                            f"\n🔧 Calling tool: {tc.get('name')} with {tc.get('args')}"
                        )
                elif msg_chunk.text:
                    print(msg_chunk.text, end="", flush=True)
            else:
                print(msg_chunk.text, end="", flush=True)
