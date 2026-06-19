import streamlit as st
from database.db import connect_to_db
from ui.state import initialize_session_state, reset_conversation
from src.ETL.etl import run_pipeline
from configs.config import get_settings
from utils.utils import enable_proxy
from src.golden_boy import context

# 0. Run ETL pipeline and setup proxy
settings = get_settings()
with connect_to_db() as connection:
    run_pipeline(
        ticker=settings.TRICKER,
        connection=connection,
        table_name="gold_price",
        start_date="2025-01-01",
        if_exists="replace",
    )
enable_proxy()

# 1. Initialize everything (runs only once per session)
initialize_session_state()

# 2. UI Configuration
st.set_page_config(page_title="Chat with memory", page_icon="🧠")
st.title("🧠 Agent with short-term-memory")

# Display thread ID (optional debug)
st.caption(f"Chat ID: `{st.session_state.thread_id[:8]}...`")

# New conversation button
if st.button("🔄 Start new chat"):
    reset_conversation()
    st.rerun()

st.divider()

# 3. Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Handle user input
if prompt := st.chat_input("Enter your message ..."):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare config for LangGraph
    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    # Get response from agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking ..."):
            token = context.current_thread_id.set(st.session_state.thread_id)

            try:
                response = st.session_state.agent.invoke(
                    {"messages": [{"role": "user", "content": prompt}]}, config=config
                )
            finally:
                context.current_thread_id.reset(token)

            final_answer = response["messages"][-1].content
            st.markdown(final_answer)

    # Append assistant response
    st.session_state.messages.append({"role": "assistant", "content": final_answer})
