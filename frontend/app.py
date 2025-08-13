import streamlit as st
import requests
from constants import SYSTEM_PROMPT
import streamlit.components.v1 as components
from streamlit_javascript import st_javascript
from dotenv import load_dotenv
from utils import chat_with_maya
import os
import json

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Maya - Beauty in a Bag", layout="centered")

# --- Session State Initialization ---
if "username" not in st.session_state:
    st.session_state.username = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "phase" not in st.session_state:
    st.session_state.phase = "start"
if "last_processed_transcript" not in st.session_state:
    st.session_state.last_processed_transcript = ""

# --- Login / Registration ---
if st.session_state.username is None:
    st.title("🌸 Maya – Beauty in a Bag")
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            res = requests.post(f"{API_BASE_URL}/login", json={"username": username, "password": password})
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
            res = requests.post(f"{API_BASE_URL}/register", json={"username": reg_user, "password": reg_pass})
            if res.status_code == 200:
                st.success("🎉 Registered! You can now log in.")
            else:
                st.error(res.json()["detail"])
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
        if "content" in msg:
            st.markdown(msg["content"])
        elif "tool_calls" in msg:
            st.markdown("_Tool call executed._")
        else:
            st.markdown("_Unknown message format._")

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
                st.audio(audio_bytes, format="audio/mp3")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# --- Voice Assistant UI ---
st.markdown("🎤 Speak or type your message")

components.html("""
<html>
  <body>
    <button id="recordBtn">🎙️ Start Recording</button>
    <p id="output" style="color:white;">Transcript will appear here...</p>
    <script>
      const recordBtn = document.getElementById('recordBtn');
      const output = document.getElementById('output');
      let mediaRecorder;
      let audioChunks = [];

      recordBtn.onclick = async () => {
        if (!mediaRecorder || mediaRecorder.state === "inactive") {
          try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            output.innerText = "Recording...";

            mediaRecorder.ondataavailable = event => {
              if (event.data.size > 0) {
                audioChunks.push(event.data);
              }
            };

            mediaRecorder.onstop = async () => {
              if (audioChunks.length === 0) {
                output.innerText = "No audio recorded";
                return;
              }

              const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
              const formData = new FormData();
              formData.append('audio', audioBlob);
              output.innerText = "Transcribing...";

              // Step 1: Transcribe audio using Deepgram
              try {
                const response = await fetch('https://maya-beauty-bag-1.onrender.com/transcribe', {
                  method: 'POST',
                  body: formData
                });

                const result = await response.json();
                if (!result.transcript) {
                  output.innerText = "No speech detected.";
                  return;
                }

                const transcript = result.transcript;
                output.innerText = transcript;

                // Step 2: Send transcript directly to FastAPI
                const username = window.parent.document.querySelector("input[key='login_user']")?.value 
                              || window.parent.document.querySelector("p").innerText.match(/Logged in as: (.+)/)?.[1];

                if (!username) {
                  output.innerText = "Not logged in";
                  return;
                }

                const saveRes = await fetch('https://maya-beauty-bag-1.onrender.com/process_voice_input', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ username, transcript })
                });

                const saveData = await saveRes.json();
                if (saveData.status === "success") {
                  // Trigger Streamlit to refresh and load new message
                  window.parent.postMessage({
                    type: 'transcript_received',
                    transcript: transcript
                  }, '*');
                } else {
                  output.innerText = "Failed to save.";
                }

              } catch (error) {
                console.error('Error:', error);
                output.innerText = "Error processing voice.";
              }
            };

            mediaRecorder.start();
            recordBtn.innerText = "⏹️ Stop Recording";
          } catch (error) {
            console.error("Recording failed:", error);
            output.innerText = "Error accessing microphone";
          }
        } else {
          mediaRecorder.stop();
          recordBtn.innerText = "🎙️ Start Recording";
        }
      };
    </script>
  </body>
</html>
""", height=250)

# Listen for transcript event
if 'js_listener_added' not in st.session_state:
    st.session_state.js_listener_added = True
    st_javascript("""
    window.addEventListener('message', function(event) {
        if (event.data && event.data.type === 'transcript_received') {
            console.log('Transcript received in parent:', event.data.transcript);
            // Trigger rerun
            const evt = new CustomEvent('streamlit:rerun');
            window.dispatchEvent(evt);
        }
    });
    """)

# Now check: has the user's conversation been updated?
user_file = os.path.join("backend", "data", "users", f"{st.session_state.username}.json") if st.session_state.username else None

last_transcript_time = st.session_state.get("last_transcript_time", 0)
transcript_detected = False

if user_file and os.path.exists(user_file):
    with open(user_file, "r") as f:
        user_data = json.load(f)
    
    conversation = user_data.get("conversation", [])
    if conversation:
        # Get the latest user message
        latest_msg = conversation[-1]
        if latest_msg["role"] == "user":
            msg_time = os.path.getmtime(user_file)  # Use file modification time
            if msg_time > last_transcript_time:
                st.session_state.last_transcript_time = msg_time
                st.session_state.pending_transcript = latest_msg["content"]
                transcript_detected = True

# Process the pending transcript
if transcript_detected and st.session_state.pending_transcript:
    transcript = st.session_state.pending_transcript
    st.session_state.pending_transcript = None  # Clear

    # Display in chat
    with st.chat_message("user"):
        st.markdown(transcript)
    st.session_state.messages.append({"role": "user", "content": transcript})

    # Get AI response
    with st.chat_message("assistant"):
        try:
            response = chat_with_maya(st.session_state.messages, username=st.session_state.username)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

            if os.path.exists("maya_response.mp3"):
                audio_bytes = open("maya_response.mp3", "rb").read()
                st.audio(audio_bytes, format="audio/mp3")

        except Exception as e:
            st.error(f"Error: {str(e)}")

    st.rerun()