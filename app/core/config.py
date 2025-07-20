from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Dopamine Detox"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/dopaminedetox")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Groq LLM Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    LLM_MODEL_NAME: str = "llama3-8b-8192" # Or another model like "mixtral-8x7b-32768"

    class Config:
        case_sensitive = True

settings = Settings()