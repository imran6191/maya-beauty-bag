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
├── backend/
│ ├── main.py # FastAPI app (auth, order, voice transcription routes)
│ ├── auth.py # User registration and login logic
│ ├── orders.py # Order saving and retrieval
│ ├── products.json # Beauty bags and products data
│
├── frontend/
│ ├── app.py # Streamlit app with text + voice chat interface
│ ├── constants.py # System prompt for OpenAI assistant
│ ├── utils.py # Product lookup, order saving, OpenAI chat logic
│
├── requirements.txt 
└── README.md