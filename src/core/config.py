from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = "CodeAron"
    VERSION: str = "0.1.0"
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    MODEL_DIR: Path = BASE_DIR / "models"
    DB_PATH: Path = BASE_DIR / "aron_memory.db"
    
    # MLX / LLM Settings
    DEFAULT_MODEL: str = "mlx-community/deepseek-coder-6.7b-instruct-4bit"
    MAX_RETRIES: int = 3
    
    class Config:
        env_prefix = "ARON_"

settings = Settings()
