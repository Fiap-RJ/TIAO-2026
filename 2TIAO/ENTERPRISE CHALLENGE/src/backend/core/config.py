import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    MODEL_NAME: str = "gemini-3.1-flash-lite"
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"

    class Config:
        env_file = ".env"

settings = Settings()