# backend/ai/tts.py
import requests
from backend.core.config import settings

def speak_response(text: str):
    url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
    headers = {
        "Authorization": f"Token {settings.DEEPGRAM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.content
        print("❌ TTS failed:", response.text)
    except Exception as e:
        print("❌ TTS error:", e)
    return None