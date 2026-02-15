import mlx_lm
import os
import sys
from typing import Optional, List, Dict
from src.core.config import settings
from rich.console import Console

console = Console()

class InferenceEngine:
    def __init__(self, model_path: Optional[str] = None):
        if not model_path:
            model_dir = settings.MODEL_DIR
            if os.path.exists(model_dir):
                local_models = [d for d in os.listdir(model_dir) if os.path.isdir(os.path.join(model_dir, d))]
                if local_models:
                    self.model_path = str(os.path.join(model_dir, local_models[0]))
                else:
                    self.model_path = settings.DEFAULT_MODEL
            else:
                self.model_path = settings.DEFAULT_MODEL
        else:
            self.model_path = model_path
            
        self.model = None
        self.tokenizer = None

    def load_model(self):
        """Memuat model secara silent dengan mengalihkan level low-level file descriptors."""
        if not self.model:
            # Simpan file descriptor asli untuk stdout dan stderr (biasanya 1 dan 2)
            null_fds = [os.open(os.devnull, os.O_RDWR) for _ in range(2)]
            save_fds = [os.dup(1), os.dup(2)]
            
            try:
                # Alihkan file descriptor 1 (stdout) dan 2 (stderr) ke /dev/null
                os.dup2(null_fds[0], 1)
                os.dup2(null_fds[1], 2)
                
                # Muat model
                self.model, self.tokenizer = mlx_lm.load(self.model_path)
            finally:
                # Kembalikan file descriptor asli
                os.dup2(save_fds[0], 1)
                os.dup2(save_fds[1], 2)
                
                # Tutup descriptor sementara
                for fd in null_fds + save_fds:
                    os.close(fd)

    def generate_stream(self, prompt: str, max_tokens: int = 2000):
        """Menghasilkan respon secara streaming (kata demi kata)."""
        if not self.model:
            self.load_model()
            
        # Alihkan stderr untuk membungkam peringatan MLX
        save_stderr = os.dup(2)
        null_fd = os.open(os.devnull, os.O_RDWR)
        try:
            os.dup2(null_fd, 2)
            
            # Gunakan stream_generate untuk MLX
            for response in mlx_lm.stream_generate(
                self.model, 
                self.tokenizer, 
                prompt=prompt, 
                max_tokens=max_tokens
            ):
                yield response.text
        finally:
            os.dup2(save_stderr, 2)
            os.close(save_stderr)
            os.close(null_fd)

    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """Menghasilkan respon dari AI."""
        if not self.model:
            self.load_model()
            
        # Alihkan lagi saat generate untuk membungkam peringatan dinamis
        null_fds = [os.open(os.devnull, os.O_RDWR) for _ in range(2)]
        save_fds = [os.dup(1), os.dup(2)]
        try:
            os.dup2(null_fds[0], 1)
            os.dup2(null_fds[1], 2)
            
            response = mlx_lm.generate(
                self.model, 
                self.tokenizer, 
                prompt=prompt, 
                max_tokens=max_tokens,
                verbose=False
            )
            return response
        finally:
            os.dup2(save_fds[0], 1)
            os.dup2(save_fds[1], 2)
            for fd in null_fds + save_fds:
                os.close(fd)
