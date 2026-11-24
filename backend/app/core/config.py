"""Core application configuration."""
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "EvidenceGraph AI"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "evidencegraph_ai_super_secret_jwt_key_replace_in_production_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'evidencegraph.db'}")

    # Qdrant Vector DB
    QDRANT_MODE: str = os.getenv("QDRANT_MODE", "local")  # "local" or "server"
    QDRANT_PATH: str = os.getenv("QDRANT_PATH", str(BASE_DIR / "qdrant_storage"))
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION_PREFIX: str = "evidencegraph_"

    # AI & Embeddings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "fastembed")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    EMBEDDING_DIMENSION: int = 384  # 384 for bge-small-en-v1.5 and all-MiniLM-L6-v2

    # Storage & Uploads
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    MAX_FILE_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt", ".md"]

    # Retrieval Defaults
    TOP_K_RETRIEVAL: int = 10
    RERANK_TOP_K: int = 5
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 100

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

# Ensure critical directories exist
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
if settings.QDRANT_MODE == "local":
    Path(settings.QDRANT_PATH).mkdir(parents=True, exist_ok=True)
