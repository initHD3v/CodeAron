from pydantic_settings import BaseSettings
from pathlib import Path
import os
import logging

class Settings(BaseSettings):
    APP_NAME: str = "CodeAron"
    VERSION: str = "0.2.1"
    
    # Path Management
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    MODEL_DIR: Path = BASE_DIR / "models"
    DB_DIR: Path = BASE_DIR / "qdrant_db"
    DB_PATH: Path = DB_DIR / "aron_symbols.db"
    LOG_DIR: Path = BASE_DIR / "logs"
    LOG_FILE: Path = LOG_DIR / "aron.log"
    
    # Create necessary dirs
    def create_dirs(self):
        for d in [self.MODEL_DIR, self.DB_DIR, self.LOG_DIR]:
            d.mkdir(parents=True, exist_ok=True)

    # Context & Project
    CURRENT_PROJECT_DIR: Path = Path(os.getcwd())
    
    # MLX / LLM Settings
    DEFAULT_MODEL: str = "mlx-community/deepseek-coder-6.7b-instruct-4bit"
    MAX_TOKENS_GEN: int = 2000
    CONTEXT_WINDOW_LIMIT: int = 24000
    
    # Indexing Settings
    IGNORED_DIRS: list = [
        '.git', '.dart_tool', 'build', '.venv', 'node_modules', 
        '__pycache__', 'dist', 'coverage', '.gradle', 'ios', 'android',
        'venv', 'env', '.idea', '.vscode'
    ]
    
    SUPPORTED_EXTENSIONS: dict = {
        '.dart': 'dart',
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.jsx': 'javascript',
        '.java': 'java',
        '.kt': 'kotlin'
    }

    class Config:
        env_prefix = "ARON_"

settings = Settings()
settings.create_dirs()

# Centralized Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler(open(os.devnull, 'w')) # Silently log to file only by default
    ]
)
