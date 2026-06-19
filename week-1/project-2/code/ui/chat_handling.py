# ui/chat_handling.py
import streamlit as st
from src.gold_agent import context


def process_user_message(prompt: str, thread_id: str, agent):
    """
    Invoke the agent with the given prompt and return the final answer.
    Handles the context variable for thread_id.
    """

    config = {"configurable": {"thread_id": thread_id}}
    token = context.current_thread_id.set(thread_id)
    try:
        response = agent.invoke(
            {"messages": [{"role": "user", "content": prompt}]}, config=config
        )
    finally:
        context.current_thread_id.reset(token)

    return response["messages"][-1].content
