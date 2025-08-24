# backend/core/config.py
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    DEEPGRAM_API_KEY: str
    DATABASE_URL: str = "backend/data/users"
    API_BASE_URL: str = "http://localhost:8000"

    model_config = {
        "env_file": Path(__file__).parent.parent.parent / ".env",
        "env_file_encoding": "utf-8"
    }

settings = Settings()