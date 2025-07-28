import os
import json

DATA_DIR = "backend/data/users"

def save_user_order(user_id, order_data):
    user_file = os.path.join(DATA_DIR, f"{user_id.replace('maya_user_', '')}.json")
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            data = json.load(f)
        data["orders"].append(order_data)
        with open(user_file, "w") as f:
            json.dump(data, f)

def get_user_history(user_id):
    user_file = os.path.join(DATA_DIR, f"{user_id.replace('maya_user_', '')}.json")
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            return json.load(f).get("orders", [])
    return []
