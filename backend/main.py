from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.auth import register_user, authenticate_user
from backend.orders import save_user_order, get_user_history
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class RegisterData(BaseModel):
    username: str
    password: str

class LoginData(BaseModel):
    username: str
    password: str

class OrderData(BaseModel):
    user_id: str
    order_data: dict

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
