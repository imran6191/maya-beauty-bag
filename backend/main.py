from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from backend.auth import register_user, authenticate_user
from backend.orders import save_user_order, get_user_history
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import tempfile
import json

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))  # Add project root to path
load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
app = FastAPI()

# Allow CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Add this near the top with other configurations
DATA_DIR = os.path.join(os.path.dirname(__file__), "data/users")
os.makedirs(DATA_DIR, exist_ok=True)  # Create directory if it doesn't exist

# Auth Models
class RegisterData(BaseModel):
    username: str
    password: str

class LoginData(BaseModel):
    username: str
    password: str

class OrderData(BaseModel):
    user_id: str
    order_data: dict

# Add this with your other imports
from pydantic import BaseModel

class TranscriptData(BaseModel):
    username: str
    transcript: str

@app.post("/register")
def register(data: RegisterData):
    if register_user(data.username, data.password):
        return {"message": "User registered."}
    raise HTTPException(status_code=400, detail="User already exists.")

@app.post("/login")
def login(data: LoginData):
    user_id = authenticate_user(data.username, data.password)
    if user_id:
        return {"user_id": user_id}
    raise HTTPException(status_code=401, detail="Invalid credentials.")

@app.post("/save_order")
def save_order(data: OrderData):
    save_user_order(data.user_id, data.order_data)
    return {"message": "Order saved."}

@app.get("/user_orders/{user_id}")
def user_orders(user_id: str):
    return {"orders": get_user_history(user_id)}

@app.post("/process_voice_input")
async def process_voice_input(data: TranscriptData):
    """Endpoint to process voice transcripts from the frontend"""
    try:
        # Get the user's current conversation state
        user_file = os.path.join(DATA_DIR, f"{data.username}.json")
        if os.path.exists(user_file):
            with open(user_file, "r") as f:
                user_data = json.load(f)
            
            # Add the new message to the conversation
            messages = user_data.get("conversation", [])
            messages.append({"role": "user", "content": data.transcript})
            
            # Save the updated conversation
            user_data["conversation"] = messages
            with open(user_file, "w") as f:
                json.dump(user_data, f)
            
            return {"status": "success", "message": "Transcript saved."}
        
        return {"status": "error", "message": "User not found"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
# Voice transcription route using Deepgram
@app.post("/transcribe")
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
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": "audio/wav",
            }
            response = requests.post("https://api.deepgram.com/v1/listen", headers=headers, data=f)
            

        if response.status_code == 200:
            transcript = response.json()["results"]["channels"][0]["alternatives"][0]["transcript"]
            return {"transcript": transcript}
        else:
            return JSONResponse(status_code=500, content={"error": "Deepgram failed", "details": response.text})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))