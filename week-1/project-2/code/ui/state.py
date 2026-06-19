import streamlit as st
import uuid

import contextvars
from langgraph.checkpoint.memory import InMemorySaver
from src.gold_agent.agents.main_agent import build_agent
from src.gold_agent import context


def initialize_session_state():
    """Initialize all Streamlit session state variables exactly once."""
    if "checkpointer" not in st.session_state:
        st.session_state.checkpointer = InMemorySaver()

    if "agent" not in st.session_state:
        st.session_state.agent = build_agent(st.session_state.checkpointer)

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []


def reset_conversation():
    """Reset the conversation thread."""
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = []
