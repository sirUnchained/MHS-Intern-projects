import uuid
import streamlit as st
from langgraph.checkpoint.memory import InMemorySaver
from src.gold_agent import build_gold_agent


def initialize_session_state():
    """Initialize all Streamlit session state variables exactly once per session."""
    if "checkpointer" not in st.session_state:
        st.session_state.checkpointer = InMemorySaver()

    if "agent" not in st.session_state:
        st.session_state.agent = build_gold_agent(st.session_state.checkpointer)

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []


def reset_conversation():
    """Start a fresh conversation thread (new UUID, cleared message history)."""
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = []
