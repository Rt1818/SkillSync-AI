from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Any


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
    CORS_ORIGINS: Any = ["http://localhost:4200", "http://localhost:3000"]
    MAX_UPLOAD_SIZE_MB: int = 10
    APP_ENV: str = "development"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip().strip("'\"")
            if v.startswith("["):
                import json
                return json.loads(v)
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
