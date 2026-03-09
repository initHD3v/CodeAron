import mlx_lm
import os
import sys
import gc
import logging
from typing import Optional, Generator, Dict
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


class InferenceConfig:
    """
    Task-specific inference configurations.
    Temperature lebih rendah untuk task yang butuh presisi tinggi.
    """
    # Coding tasks - presisi maksimal
    CODING = {
        "temperature": 0.2,
        "max_tokens": 2000,
        "top_p": 0.9,
        "description": "Code generation, modification, and debugging"
    }
    
    # Analysis tasks - balanced antara kreativitas dan akurasi
    ANALYSIS = {
        "temperature": 0.3,
        "max_tokens": 1500,
        "top_p": 0.9,
        "description": "Project analysis and code review"
    }
    
    # Planning tasks - butuh struktur yang jelas
    PLANNING = {
        "temperature": 0.4,
        "max_tokens": 1000,
        "top_p": 0.9,
        "description": "Task planning and architecture design"
    }
    
    # Chat/General - lebih kreatif untuk conversational
    CHAT = {
        "temperature": 0.7,
        "max_tokens": 500,
        "top_p": 0.95,
        "description": "General conversation and greetings"
    }
    
    # Shell commands - deterministik untuk command execution
    SHELL = {
        "temperature": 0.1,
        "max_tokens": 300,
        "top_p": 0.85,
        "description": "Shell command generation"
    }
    
    @classmethod
    def get_config(cls, task_type: str) -> Dict:
        """Get config for specific task type."""
        task_type_upper = task_type.upper()
        if hasattr(cls, task_type_upper):
            return getattr(cls, task_type_upper)
        # Default to CODING for unknown tasks (safer for code tasks)
        return cls.CODING

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
                # Prioritaskan Qwen, lalu Llama
                priority = ["qwen", "llama"]
                best_candidate = candidates[0]
                
                for p in priority:
                    for c in candidates:
                        if p in c.lower() and '4bit' in c.lower():
                            return str(os.path.join(model_dir, c))
                
                return str(os.path.join(model_dir, best_candidate))
        
        # 3. Fallback (akan memicu download jika menggunakan string HF repo)
        return settings.DEFAULT_MODEL

    def load_model(self):
        """Memuat model ke memori jika belum dimuat dengan validasi RAM."""
        if self.model is not None:
            return

        import psutil
        vm = psutil.virtual_memory()
        # Jika RAM tersedia < 1GB (dalam bytes), log warning
        if vm.available < (1024 ** 3):
            logger.warning(f"Low RAM detected ({vm.available / (1024**3):.2f} GB). Model loading might be slow or unstable.")

        logger.info(f"Loading model from {self.model_path}...")
        try:
            # Force GC sebelum load
            gc.collect()
            if mx: mx.clear_cache()

            # Load Model & Tokenizer
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

    def generate_stream(self, prompt: str, task_type: str = "coding", max_tokens: int = None, temp: float = None, stop_sequences: list = None) -> Generator[str, None, None]:
        """
        Generator streaming untuk respon AI dengan task-specific settings.
        
        Args:
            prompt: Input prompt
            task_type: Type of task (coding, analysis, planning, chat, shell)
            max_tokens: Override max tokens (optional)
            temp: Override temperature (optional)
            stop_sequences: Stop sequences to halt generation
        """
        if not self.model:
            self.load_model()

        # Get task-specific config
        config = InferenceConfig.get_config(task_type)
        
        # Use provided values or fallback to config
        temperature = temp if temp is not None else config["temperature"]
        tokens = max_tokens if max_tokens is not None else config["max_tokens"]
        top_p = config["top_p"]

        # Proteksi Context Window Sederhana
        if len(prompt) > settings.CONTEXT_WINDOW_LIMIT:
            logger.warning("Prompt too long, truncating...")
            prompt = prompt[-settings.CONTEXT_WINDOW_LIMIT:]

        logger.debug(f"Generating with task_type={task_type}, temp={temperature}, max_tokens={tokens}")

        try:
            # Gunakan sampler dari mlx_lm.sample_utils dengan temperature dan top_p
            sampler = make_sampler(temp=temperature, top_p=top_p) if make_sampler else None

            # Gunakan stream_generate dari mlx_lm
            stream = mlx_lm.stream_generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=tokens,
                sampler=sampler
            )
            
            generated_text = ""
            for response in stream:
                current_chunk = str(response.text)
                new_total_text = generated_text + current_chunk
                
                if stop_sequences:
                    should_stop = False
                    for stop in stop_sequences:
                        if stop in new_total_text:
                            stop_index = new_total_text.find(stop)
                            safe_to_send_total = new_total_text[:stop_index]
                            safe_chunk = safe_to_send_total[len(generated_text):]
                            if safe_chunk:
                                yield safe_chunk
                            should_stop = True
                            break
                    if should_stop:
                        break
                
                # Deteksi Repetisi (Loop Protection)
                lines = new_total_text.splitlines()
                if len(lines) > 5:
                    last_three = lines[-3:]
                    if len(set(last_three)) == 1 and len(last_three[0].strip()) > 5:
                        logger.warning("Repetition detected, stopping generation.")
                        break
                
                generated_text = new_total_text
                yield current_chunk
                
        except Exception as e:
            logger.error(f"Generation error: {e}")
            yield f"\n[System Error: {str(e)}]\n"
        finally:
            # Cleanup ringan setelah setiap request
            if mx: mx.eval(None) # Ensure computation is done? (Not strictly needed in stream)
            pass

    def generate_oneshot(self, prompt: str, task_type: str = "coding", max_tokens: int = None, temp: float = None) -> str:
        """
        Generate full response sekaligus (bukan streaming) dengan task-specific settings.
        
        Args:
            prompt: Input prompt
            task_type: Type of task (coding, analysis, planning, chat, shell)
            max_tokens: Override max tokens (optional)
            temp: Override temperature (optional)
        """
        if not self.model:
            self.load_model()

        # Get task-specific config
        config = InferenceConfig.get_config(task_type)
        
        # Use provided values or fallback to config
        temperature = temp if temp is not None else config["temperature"]
        tokens = max_tokens if max_tokens is not None else config["max_tokens"]
        top_p = config["top_p"]

        logger.debug(f"Oneshot generating with task_type={task_type}, temp={temperature}, max_tokens={tokens}")

        try:
            # Create sampler with task-specific settings
            sampler = make_sampler(temp=temperature, top_p=top_p) if make_sampler else None
            
            return mlx_lm.generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=tokens,
                sampler=sampler,
                verbose=False
            )
        except Exception as e:
            logger.error(f"Oneshot generation error: {e}")
            return ""
