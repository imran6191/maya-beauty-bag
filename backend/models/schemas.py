# backend/models/schemas.py
from pydantic import BaseModel
from typing import Dict, Any

class RegisterData(BaseModel):
    username: str
    password: str

class LoginData(BaseModel):
    username: str
    password: str

class OrderData(BaseModel):
    user_id: str
    order: Dict[str, Any]

class TranscriptData(BaseModel):
    username: str
    transcript: str