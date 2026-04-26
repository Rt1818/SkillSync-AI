from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"

    # Tavily
    TAVILY_API_KEY: str

    # MongoDB
    MONGODB_URI: str
    MONGODB_DB_NAME: str = "skillsync"

    # App
    CORS_ORIGINS: List[str] = ["http://localhost:4200", "http://localhost:3000"]
    MAX_UPLOAD_SIZE_MB: int = 10
    APP_ENV: str = "development"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
