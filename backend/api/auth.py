# backend/api/auth.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.core.security import hash_password
from backend.utils.file_store import read_user_data, write_user_data

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterData(BaseModel):
    username: str
    password: str

class LoginData(BaseModel):
    username: str
    password: str


@router.post("/register")
def register(data: RegisterData):
    user_data = read_user_data(data.username)
    
    # ❌ Was: if user: → variable not defined
    # ✅ Fix: Check if user_data exists
    if user_data:
        raise HTTPException(status_code=400, detail="User already exists")
    
    write_user_data(data.username, {
        "user_id": f"maya_user_{data.username}",
        "password": hash_password(data.password),
        "orders": [],
        "conversation": []
    })
    return {"message": "User registered."}


@router.post("/login")
def login(data: LoginData):
    user_data = read_user_data(data.username)
    
    # Check if user exists and password is valid
    if not user_data or "password" not in user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if user_data["password"] != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"user_id": user_data["user_id"]}