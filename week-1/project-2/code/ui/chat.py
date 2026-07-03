from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import AIMessageChunk
from langgraph.graph.state import CompiledStateGraph


async def process_user_message(prompt: str, thread_id: str, agent: CompiledStateGraph):
    """
    Invoke the agent with the given prompt and get the final answer with stream!

    Args:
        prompt: The user's message.
        thread_id: Conversation thread identifier (for memory isolation).
        agent: The compiled LangGraph agent.
    """
    config = RunnableConfig({"configurable": {"thread_id": thread_id}})

    # We only need the message (chunk) for now
    for chunk, _ in agent.stream(
        {"messages": [{"role": "user", "content": prompt}]},
        config=config,
        stream_mode="messages",
    ):
        if isinstance(chunk, AIMessageChunk) and chunk.content:
            yield chunk.content
