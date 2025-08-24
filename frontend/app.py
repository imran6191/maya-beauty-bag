# frontend/app.py
import streamlit as st
import requests
from prompts import SYSTEM_PROMPT
import streamlit.components.v1 as components
from dotenv import load_dotenv
from utils import chat_with_maya
import os
import sys
from pathlib import Path
import time
from streamlit import components
import base64

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))
load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Maya - Beauty in a Bag", layout="centered")

# --- Session State Initialization ---
if "username" not in st.session_state:
    st.session_state.username = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_ai_response" not in st.session_state:
    st.session_state.last_ai_response = ""

# --- Login / Registration ---
if st.session_state.username is None:
    st.title("🌸 Maya – Beauty in a Bag")
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            try:
                res = requests.post(f"{API_BASE_URL}/api/auth/login", json={"username": username, "password": password})
                if res.status_code == 200:
                    st.session_state.username = username
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    try:
                        st.error(res.json().get("detail", "Login failed"))
                    except Exception:
                        st.error(f"Server error: {res.status_code}")
            except Exception as e:
                st.error(f"Connection failed: {str(e)}")
        
    with tab2:
        reg_user = st.text_input("New Username", key="reg_user")
        reg_pass = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register"):
            try:
                res = requests.post(f"{API_BASE_URL}/api/auth/register", json={"username": reg_user, "password": reg_pass})
                if res.status_code == 200:
                    st.success("🎉 Registered! You can now log in.")
                else:
                    try:
                        st.error(res.json().get("detail", "Registration failed"))
                    except Exception:
                        st.error(f"Server error: {res.status_code}")
            except Exception as e:
                st.error(f"Connection failed: {str(e)}")
    st.stop()

# --- Sidebar Logout ---
with st.sidebar:
    st.write(f"👤 Logged in as: {st.session_state.username}")
    if st.button("Logout"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# --- Initialize Conversation ---
if not st.session_state.messages or st.session_state.messages[0].get("content") != SYSTEM_PROMPT:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "Hey love, I'm Maya. This isn't just beauty — it's a moment just for you. Let's start with your bag. ✨ Which one calls to you today?"}
    ]

# --- Display Conversation ---
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and os.path.exists("maya_response.mp3"):
            audio_bytes = open("maya_response.mp3", "rb").read()
            components.v1.html(
    f"""
    <audio controls style="width: 100%;">
        <source src="data:audio/mp3;base64,{base64.b64encode(audio_bytes).decode()}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """,
    height=80
)

# --- Text Input (User Types) ---
if user_input := st.chat_input("Your reply..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        try:
            response = chat_with_maya(st.session_state.messages, username=st.session_state.username)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

            if os.path.exists("maya_response.mp3"):
                audio_bytes = open("maya_response.mp3", "rb").read()
                components.v1.html(
    f"""
    <audio controls style="width: 100%;">
        <source src="data:audio/mp3;base64,{base64.b64encode(audio_bytes).decode()}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """,
    height=80
)
        except Exception as e:
            st.error(f"Error: {str(e)}")

# --- Voice Assistant with WebSocket ---
st.markdown("🎤 Speak or type your message")

voice_html = f"""
<html>
  <body style="background:transparent; padding:0; margin:0;">
    <button id="recordBtn" style="
      width: 100%; padding: 10px; font-size: 16px; border: none; border-radius: 8px; 
      background: #0000ff; color: white; cursor: pointer; margin-bottom: 8px;
    ">
      🎙️ Start Recording
    </button>
    <p id="output" style="color: white; font-size: 14px;">
      Ready to record...
    </p>

    <script>
      const recordBtn = document.getElementById('recordBtn');
      const output = document.getElementById('output');
      let mediaRecorder;
      let audioChunks = [];

      function connect() {{
        const username = "{st.session_state.username}";
        const socket = new WebSocket("ws://localhost:8000/ws/" + username);

        socket.onopen = () => {{
          output.innerText = "✅ Connected";
        }};

        socket.onclose = () => {{
          output.innerText = "🔁 Disconnected";
          setTimeout(connect, 3000);
        }};

        socket.onerror = (err) => {{
          console.error("WebSocket error:", err);
        }};

        window.socket = socket;
      }}

      connect();

      recordBtn.onclick = async () => {{
        if (!mediaRecorder || mediaRecorder.state === "inactive") {{
          try {{
            const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            output.innerText = "🔴 Recording...";
            recordBtn.innerText = "⏹️ Stop Recording";

            mediaRecorder.ondataavailable = (e) => {{
              if (e.data.size > 0) audioChunks.push(e.data);
            }};

            mediaRecorder.onstop = async () => {{
              if (audioChunks.length === 0) return;

              const audioBlob = new Blob(audioChunks, {{ type: 'audio/wav' }});
              const formData = new FormData();
              formData.append('audio', audioBlob);
              output.innerText = "Transcribing...";

              const res = await fetch('http://localhost:8000/api/voice/transcribe', {{
                method: 'POST',
                body: formData
              }});

              const result = await res.json();
              const transcript = result.transcript;

              if (transcript && window.socket.readyState === WebSocket.OPEN) {{
                console.log('📤 Sending transcript:', transcript);
                window.socket.send(transcript);
              }}
            }};

            mediaRecorder.start();
          }} catch (err) {{
            output.innerText = "Mic denied";
            console.error(err);
          }}
        }} else {{
          mediaRecorder.stop();
          recordBtn.innerText = "🎙️ Start Recording";
        }}
      }};
    </script>
  </body>
</html>
"""

components.v1.html(voice_html, height=150)

# --- Poll for AI Response from File ---
def get_ai_response():
    try:
        path = f"backend/data/users/{st.session_state.username}_ai_response.txt"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            return content if content else None
        return None
    except Exception as e:
        print("Error reading AI response file:", e)
        return None

# Read the file
file_response = get_ai_response()

# Only process if it's new
if file_response and file_response != st.session_state.get("last_ai_response"):
    st.session_state.last_ai_response = file_response

    # Add to chat
    st.session_state.messages.append({"role": "user", "content": "🎤 Voice message"})
    st.session_state.messages.append({"role": "assistant", "content": file_response})

    # Show in chat
    with st.chat_message("user"):
        st.markdown("🎤 Voice message")
    with st.chat_message("assistant"):
        st.markdown(file_response)
        if os.path.exists("maya_response.mp3"):
            audio_bytes = open("maya_response.mp3", "rb").read()
            components.v1.html(
    f"""
    <audio controls  style="width: 100%;">
        <source src="data:audio/mp3;base64,{base64.b64encode(audio_bytes).decode()}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """,
    height=80
)

    st.rerun()

# --- Auto-refresh ---
time.sleep(2)
st.rerun()