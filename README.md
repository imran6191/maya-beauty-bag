# 🌸 Maya – Beauty in a Bag (Voice-Enabled AI Beauty Assistant)

Maya is a fully functional, personalized beauty assistant built with FastAPI, Streamlit, and OpenAI. Users can interact with Maya using **text or voice**, select beauty bags and products, and receive AI-powered affirmations and product suggestions.

---

## ✨ Features

- 👜 Select from curated beauty bags (e.g., *The Bold Bag*, *The Soft Reset*)
- 💄 Choose products by category (foundation, lipstick, etc.)
- 💬 AI chatbot trained with a structured system prompt
- 🎙️ Voice input using JavaScript + Deepgram for transcription
- 📦 Orders saved per user
- 🔐 Login & registration system
- 🧠 OpenAI assistant using function-calling for structured flow

---

### Project Structure

maya_beauty_bag/
│
├── backend/
│ ├── init.py
│ ├── main.py # FastAPI app & WebSocket routes
│ ├── api/
│ │ ├── auth.py # /register, /login
│ │ ├── voice.py # /transcribe, /ws
│ │ └── orders.py # /save_order, /user_orders
│ │
│ ├── core/
│ │ ├── config.py # Environment settings
│ │ ├── security.py # Password hashing
│ │ └── websocket_manager.py # WebSocket manager
│ │
│ ├── ai/
│ │ ├── agent.py # chat_with_maya logic
│ │ ├── functions.py # get_bag_options, etc.
│ │ ├── prompts.py # SYSTEM_PROMPT
│ │ └── tts.py # Deepgram TTS
│ │
│ ├── models/
│ │ └── schemas.py # Pydantic models
│ │
│ ├── data/
│ │ ├── users/ # JSON files per user
│ │ └── products.json # Bag & product catalog
│ │
│ └── utils/
│ └── file_store.py # Read/write user data
│
├── frontend/
│ ├── app.py # Streamlit UI
│ ├── components/
│ │ ├── voice_widget.html # Embedded voice recorder
│ │
│ └── utils/
│ └── api_client.py # Backend API calls
│
├── .env # Environment variables
├── requirements.txt # Dependencies
├── README.md
└── docker-compose.yml (optional)