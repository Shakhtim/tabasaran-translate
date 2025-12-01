from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    DATABASE_PATH: Path = DATA_DIR / "dictionary.db"
    CHROMA_PATH: Path = DATA_DIR / "chroma"

    # API
    API_PREFIX: str = "/api"
    DEBUG: bool = True

    # LLM Server (GPU)
    LLM_SERVER_URL: str = "http://localhost:11434"  # Ollama default
    LLM_MODEL: str = "mistral:7b"
    LLM_TIMEOUT: int = 30

    # Vector search
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    # Translation
    MAX_TEXT_LENGTH: int = 5000
    FUZZY_THRESHOLD: int = 2  # Levenshtein distance

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
