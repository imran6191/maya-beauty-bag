# backend/api/voice.py
from backend.core.config import settings
from fastapi import APIRouter, File, UploadFile
from backend.core.websocket_manager import manager
import requests
import os
import tempfile

router = APIRouter(prefix="/voice", tags=["Voice"])

@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    try:
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            contents = await audio.read()
            tmp.write(contents)
            tmp_path = tmp.name

        # Send to Deepgram
        with open(tmp_path, "rb") as f:
            headers = {
                "Authorization": f"Token {settings.DEEPGRAM_API_KEY}",
                "Content-Type": "audio/wav",
            }
            response = requests.post(
                "https://api.deepgram.com/v1/listen",
                headers=headers,
                data=f
            )

        # Clean up temp file
        os.unlink(tmp_path)

        if response.status_code == 200:
            transcript = response.json()["results"]["channels"][0]["alternatives"][0]["transcript"]
            return {"transcript": transcript}
        else:
            return {"error": "Deepgram transcription failed", "details": response.text}

    except Exception as e:
        return {"error": str(e)}