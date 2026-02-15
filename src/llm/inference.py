import mlx_lm
from typing import Optional, List, Dict
from src.core.config import settings

class InferenceEngine:
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or settings.DEFAULT_MODEL
        self.model = None
        self.tokenizer = None

    def load_model(self):
        """Memuat model ke memori Apple Silicon."""
        if not self.model:
            # Menggunakan mlx_lm untuk load model native
            self.model, self.tokenizer = mlx_lm.load(self.model_path)

    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """Menghasilkan respon dari prompt."""
        if not self.model:
            self.load_model()
            
        response = mlx_lm.generate(
            self.model, 
            self.tokenizer, 
            prompt=prompt, 
            max_tokens=max_tokens,
            verbose=False
        )
        return response
