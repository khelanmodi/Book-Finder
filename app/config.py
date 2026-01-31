"""Application configuration settings."""
from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "BookFinder - Book Similarity API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DB_NAME: str = "bookfinder"

    # OpenAI Embeddings
    OPENAI_KEY: str = ""
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIM: int = 1536  # text-embedding-3-small dimensions

    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: str = '["*"]'  # JSON string

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS from JSON string."""
        try:
            return json.loads(self.ALLOWED_ORIGINS)
        except:
            return ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
