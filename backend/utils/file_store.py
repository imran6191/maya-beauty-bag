# backend/utils/file_store.py
import json
import os
from backend.core.config import settings

def read_user_data(username: str):
    user_dir = settings.DATABASE_URL
    os.makedirs(user_dir, exist_ok=True)
    file_path = os.path.join(user_dir, f"{username}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return None

def write_user_data(username: str, data: dict):
    user_dir = settings.DATABASE_URL
    os.makedirs(user_dir, exist_ok=True)
    file_path = os.path.join(user_dir, f"{username}.json")
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)