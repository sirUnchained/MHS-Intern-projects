# app.py
import streamlit as st
from ui.state import initialize_session_state, reset_conversation
from ui.backend import setup_backend
from ui.chat import process_user_message
from helpers.helpers import plot_gold_prices

# ----- Backend Setup (ETL & proxy) -----
data = setup_backend()

# ----- Session State Initialization -----
initialize_session_state()

# ----- UI Configuration -----
st.set_page_config(page_title="Chat with memory", page_icon="🧠")
st.title("🧠 Agent with short-term-memory")
st.caption(f"Chat ID: `{st.session_state.thread_id[:8]}...`")

fig = plot_gold_prices(data)
st.pyplot(fig)

if st.button("🔄 Start new chat"):
    reset_conversation()
    st.rerun()

st.divider()

# ----- Display Chat History -----
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ----- Handle User Input -----
if prompt := st.chat_input("Enter your message ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking ..."):
            final_answer = process_user_message(
                prompt, st.session_state.thread_id, st.session_state.agent
            )
        st.markdown(final_answer)

    st.session_state.messages.append({"role": "assistant", "content": final_answer})
