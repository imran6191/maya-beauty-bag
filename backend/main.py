import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket
from backend.api.auth import router as auth_router
from backend.api.voice import router as voice_router
from backend.api.orders import router as orders_router
from backend.core.websocket_manager import manager

app = FastAPI(title="Maya Beauty Bag Backend", version="1.0")

# Add CORS middleware for HTTP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # ← Allow Streamlit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(voice_router, prefix="/api")
app.include_router(orders_router, prefix="/api")

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket, username)
    try:
        while True:
            data = await websocket.receive_text()
            print("data received in main.py", data)
            await manager.handle_transcript(username, data)  # ✅ This calls chat_with_maya
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        manager.disconnect(username)

@app.get("/")
def read_root():
    return {"message": "🌸 Maya is glowing. Visit /api/docs"}