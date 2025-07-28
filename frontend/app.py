import streamlit as st
from utils import chat_with_maya
from constants import SYSTEM_PROMPT

# Initialize session state
if "llm_messages" not in st.session_state:
    st.session_state.llm_messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# Display chat history
for msg in st.session_state.llm_messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# ✅ Define input before use
user_input = st.chat_input("Type your response here...")

if user_input:
    # Show user's message
    st.chat_message("user").markdown(user_input)
    st.session_state.llm_messages.append({"role": "user", "content": user_input})

    # Get assistant's reply
    response = chat_with_maya(st.session_state.llm_messages)
    st.chat_message("assistant").markdown(response)
    st.session_state.llm_messages.append({"role": "assistant", "content": response})