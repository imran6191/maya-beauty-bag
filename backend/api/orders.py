# backend/api/orders.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.utils.file_store import read_user_data, write_user_data

router = APIRouter(prefix="/orders", tags=["Orders"])

# Model for saving order
class OrderData(BaseModel):
    user_id: str
    order_data: dict

# Endpoint: Save order
@router.post("/save_order")
def save_order( OrderData):
    username = data.user_id.replace("maya_user_", "")
    user_data = read_user_data(username)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data["orders"].append(data.order_data)
    write_user_data(username, user_data)
    
    return {"message": "Order saved."}

# Endpoint: Get user order history
@router.get("/user_orders/{user_id}")
def user_orders(user_id: str):
    username = user_id.replace("maya_user_", "")
    user_data = read_user_data(username)
    
    if not user:
        return {"orders": []}
    
    return {"orders": user_data.get("orders", [])}