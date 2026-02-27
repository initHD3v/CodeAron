import os
import mlx_lm
from PIL import Image
from pathlib import Path
from typing import Optional
from rich.console import Console
from src.core.config import settings

console = Console()

class VisionEngine:
    """Mesin untuk menganalisis gambar menggunakan Vision Language Models (VLM)."""
    
    def __init__(self, model_path: Optional[str] = None):
        # Default ke model vision ringan jika tersedia
        self.model_path = model_path or os.path.join(settings.MODEL_DIR, "moondream2-mlx")
        self.model = None
        self.tokenizer = None

    def load_model(self):
        """Memuat model vision."""
        if not self.model:
            if not os.path.exists(self.model_path):
                console.print(f"[bold red]Error:[/bold red] Model Vision tidak ditemukan di {self.model_path}")
                console.print("[dim]Gunakan '/model download moondream2' (fitur masa depan) atau unduh manual ke folder models.[/dim]")
                return False
            
            try:
                self.model, self.tokenizer = mlx_lm.load(self.model_path)
                return True
            except Exception as e:
                console.print(f"[bold red]Gagal memuat model vision:[/bold red] {str(e)}")
                return False

    def analyze_image(self, image_path: str, prompt: str = "Describe this image in detail for a Flutter developer.") -> str:
        """Menganalisis gambar berdasarkan prompt yang diberikan."""
        if not self.load_model():
            # Fallback: Minta user deskripsikan gambar
            console.print("[yellow]⚠ Model vision belum terinstall.[/yellow]")
            console.print("[dim]  Untuk enable vision analysis, download model dengan:[/dim]")
            console.print("[dim]  python3 -c \"from huggingface_hub import snapshot_download; snapshot_download('mlx-community/moondream2-4bit', local_dir='models/moondream2-mlx')\"[/dim]\n")
            
            # Fallback ke deskripsi manual
            return f"**Image Path:** {image_path}\n\n**Note:** Vision model belum terinstall. Silakan deskripsikan gambar ini secara manual atau install model vision terlebih dahulu.\n\n**File Info:**\n- Size: {os.path.getsize(image_path) / 1024:.1f} KB\n- Format: {os.path.splitext(image_path)[1].upper()}"

        try:
            image = Image.open(image_path)
            response = mlx_lm.generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                image=image,
                max_tokens=500
            )
            return response
        except Exception as e:
            return f"Error saat analisis gambar: {str(e)}"
