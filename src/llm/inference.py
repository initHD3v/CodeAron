import mlx_lm
import os
import sys
import gc
import logging
from typing import Optional, Generator
from src.core.config import settings

# Setup logging
logger = logging.getLogger("InferenceEngine")

try:
    import mlx.core as mx
    from mlx_lm.sample_utils import make_sampler
except ImportError:
    mx = None
    make_sampler = None
    logger.warning("MLX or mlx-lm sample_utils not found. Inference will fail.")

class InferenceEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InferenceEngine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.model_path = self._resolve_model_path()
        self.model = None
        self.tokenizer = None
        self._initialized = True
        logger.info(f"InferenceEngine initialized. Model target: {self.model_path}")

    def _resolve_model_path(self) -> str:
        """Menentukan path model yang valid."""
        # 1. Cek dari Config/Env
        if settings.DEFAULT_MODEL and os.path.exists(settings.DEFAULT_MODEL):
            return settings.DEFAULT_MODEL
            
        # 2. Cek folder models/ secara otomatis
        model_dir = settings.MODEL_DIR
        if os.path.exists(model_dir):
            # Cari folder yang valid (bukan hidden)
            candidates = [
                d for d in os.listdir(model_dir) 
                if os.path.isdir(os.path.join(model_dir, d)) and not d.startswith('.')
            ]
            if candidates:
                # Prioritaskan yang mengandung 'mlx' atau '4bit'
                best_candidate = candidates[0]
                for c in candidates:
                    if 'mlx' in c.lower() and '4bit' in c.lower():
                        best_candidate = c
                        break
                return str(os.path.join(model_dir, best_candidate))
        
        # 3. Fallback (akan memicu download jika menggunakan string HF repo)
        return settings.DEFAULT_MODEL

    def load_model(self):
        """Memuat model ke memori jika belum dimuat."""
        if self.model is not None:
            return

        logger.info(f"Loading model from {self.model_path}...")
        try:
            # Force GC sebelum load
            gc.collect()
            if mx: mx.clear_cache()

            # Load Model & Tokenizer
            # mlx_lm.load secara otomatis menangani config (trust_remote_code biasanya tidak perlu untuk MLX format lokal)
            self.model, self.tokenizer = mlx_lm.load(self.model_path)
            
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.critical(f"Failed to load model: {e}")
            raise RuntimeError(f"Could not load AI model: {e}")

    def unload_model(self):
        """Melepas model dari memori secara paksa."""
        if self.model:
            del self.model
            del self.tokenizer
            self.model = None
            self.tokenizer = None
            
            if mx: mx.clear_cache()
            gc.collect()
            logger.info("Model unloaded from memory.")

    def generate_stream(self, prompt: str, max_tokens: int = 1000, temp: float = 0.7, stop_sequences: list = None) -> Generator[str, None, None]:
        """Generator streaming untuk respon AI."""
        if not self.model:
            self.load_model()

        # Proteksi Context Window Sederhana
        if len(prompt) > settings.CONTEXT_WINDOW_LIMIT:
            logger.warning("Prompt too long, truncating...")
            prompt = prompt[-settings.CONTEXT_WINDOW_LIMIT:]

        try:
            # Gunakan sampler dari mlx_lm.sample_utils
            sampler = make_sampler(temp=temp) if make_sampler else None
            
            # Gunakan stream_generate dari mlx_lm
            # max_tokens di sini adalah output tokens
            # Stop sequences mencegah model "bicara sendiri" sebagai User
            stream = mlx_lm.stream_generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                sampler=sampler
            )
            
            generated_text = ""
            for response in stream:
                generated_text += response.text
                
                if stop_sequences:
                    should_stop = False
                    for stop in stop_sequences:
                        if stop in generated_text:
                            # Jika ditemukan stop sequence, kita potong teks hingga akhir stop sequence tersebut
                            # dan kirimkan sisanya sebelum berhenti
                            should_stop = True
                            break
                    if should_stop:
                        # Kirimkan chunk terakhir (yang mengandung bagian dari stop sequence)
                        yield response.text
                        break
                
                yield response.text
                
        except Exception as e:
            logger.error(f"Generation error: {e}")
            yield f"\n[System Error: {str(e)}]\n"
        finally:
            # Cleanup ringan setelah setiap request
            if mx: mx.eval(None) # Ensure computation is done? (Not strictly needed in stream)
            pass

    def generate_oneshot(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate full response sekaligus (bukan streaming)."""
        if not self.model:
            self.load_model()
            
        try:
            return mlx_lm.generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                verbose=False
            )
        except Exception as e:
            logger.error(f"Oneshot generation error: {e}")
            return ""
