from langchain_core.runnables.config import RunnableConfig


def process_user_message(prompt: str, thread_id: str, agent) -> str:
    """
    Invoke the agent with the given prompt and return the final answer.

    Args:
        prompt: The user's message.
        thread_id: Conversation thread identifier (for memory isolation).
        agent: The compiled LangGraph agent.

    Returns:
        The agent's final text response.
    """
    config = RunnableConfig({"configurable": {"thread_id": thread_id}})
    # token = context.current_thread_id.set(thread_id)

    try:
        response = agent.invoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config=config,
        )
    finally:
        pass
        # context.current_thread_id.reset(token)

    return response["messages"][-1].content
