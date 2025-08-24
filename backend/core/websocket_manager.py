# backend/core/websocket_manager.py

from fastapi import WebSocket
from typing import Dict
from backend.ai.agent import chat_with_maya
from backend.utils.file_store import read_user_data, write_user_data
from backend.ai.prompts import SYSTEM_PROMPT
import json
import os

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.conversations = {}

    async def connect(self, websocket: WebSocket, username: str):
        print(f"🔌 WebSocket connecting for {username}")
        await websocket.accept()
        self.active_connections[username] = websocket

        # Load conversation
        user_data = read_user_data(username)
        messages = user_data.get("conversation", []) if user_data else []
        self.conversations[username] = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        print(f"📥 Loaded {len(messages)} messages for {username}")

    def disconnect(self, username: str):
        if username in self.active_connections:
            del self.active_connections[username]
        if username in self.conversations:
            del self.conversations[username]
        print(f"🔌 WebSocket disconnected for {username}")

    async def handle_transcript(self, username: str, transcript: str):
        print(f"🎙️ Received transcript websocket manager from {username}: {transcript}")

        if username not in self.conversations:
            print(f"❌ No conversation found for {username}")
            return

        full_messages = self.conversations[username]
        full_messages.append({"role": "user", "content": transcript})

        # Get AI response
        ai_response = chat_with_maya(full_messages, username=username)

        # ✅ Save AI response to file
        try:
            response_path = f"backend/data/users/{username}_ai_response.txt"
            with open(response_path, "w", encoding="utf-8") as f:
                f.write(ai_response)
            print(f"✅ AI response saved to {response_path}")
        except Exception as e:
            print(f"❌ Failed to save AI response: {e}")

        # ✅ Send response back via WebSocket
        await self.send_personal_message(ai_response, username)

        # Save conversation
        user_data = read_user_data(username)
        if user_data:
            user_data["conversation"] = [m for m in full_messages if m["role"] != "system"]
            write_user_data(username, user_data)

    # backend/core/websocket_manager.py

    async def send_personal_message(self, message: str, username: str):
        connection = self.active_connections.get(username)
        if connection:
            await connection.send_text(message)
            print(f"📤 Sent to {username}: {message[:50]}...")
            
            # ✅ Save to file
            try:
                with open(f"backend/data/users/{username}_ai_response.txt", "w", encoding="utf-8") as f:
                    f.write(message)
                print(f"✅ AI response saved to backend/data/users/{username}_ai_response.txt")
            except Exception as e:
                print(f"❌ Failed to save AI response: {e}")
        else:
            print(f"❌ No connection to send to {username}")

# Create a global instance
manager = WebSocketManager()