import streamlit as st
import os
import requests
from datetime import datetime
from constants import SYSTEM_PROMPT
from utils import (
    get_function_specs,
    chat_with_maya,
    get_bag_options,
    get_products_by_category,
    create_checkout_summary
)

# Streamlit page setup
st.set_page_config(page_title="Maya - Beauty in a Bag", layout="centered")

# Initialize session state
if "username" not in st.session_state:
    st.session_state.username = None
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.phase = "start"

# Auth UI
if st.session_state.username is None:
    st.title("🌸 Maya – Beauty in a Bag")

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            res = requests.post("https://maya-beauty-bag-1.onrender.com/login", json={"username": username, "password": password})
            if res.status_code == 200:
                st.session_state.username = username
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error(res.json()["detail"])

    with tab2:
        reg_user = st.text_input("New Username", key="reg_user")
        reg_pass = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register"):
            res = requests.post("https://maya-beauty-bag-1.onrender.com/register", json={"username": reg_user, "password": reg_pass})
            if res.status_code == 200:
                st.success("🎉 Registered! You can now log in.")
            else:
                st.error(res.json()["detail"])
    st.stop()

# Sidebar logout
with st.sidebar:
    st.write(f"👤 Logged in as: {st.session_state.username}")
    if st.button("Logout"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# Initialize conversation
if not st.session_state.messages:
    st.session_state.messages.append({"role": "system", "content": SYSTEM_PROMPT})
    st.session_state.messages.append({"role": "assistant", "content": "Hey love, I'm Maya. This isn't just beauty — it's a moment just for you. Let's start with your bag. ✨ Which one calls to you today?"})

# Display conversation
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        if "content" in msg:
            st.markdown(msg["content"])
        elif "tool_calls" in msg:
            st.markdown("_Tool call executed._")
        else:
            st.markdown("_Unknown message format._")

# Input
if user_input := st.chat_input("Your reply..."):
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        response = chat_with_maya(st.session_state.messages, username=st.session_state.username)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})