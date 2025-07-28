import hashlib
import json
import os

DATA_DIR = "backend/data/users"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    user_file = os.path.join(DATA_DIR, f"{username}.json")
    if os.path.exists(user_file):
        return False
    data = {
        "user_id": f"maya_user_{username}",
        "password": hash_password(password),
        "orders": []
    }
    with open(user_file, "w") as f:
        json.dump(data, f)
    return True

def authenticate_user(username, password):
    user_file = os.path.join(DATA_DIR, f"{username}.json")
    if not os.path.exists(user_file):
        return None
    with open(user_file, "r") as f:
        data = json.load(f)
    if data["password"] == hash_password(password):
        return data["user_id"]
    return None
