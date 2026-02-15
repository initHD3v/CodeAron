from typing import List, Dict
import os
from src.core.config import settings
from rich.table import Table
from rich.console import Console

console = Console()

class ModelHub:
    def __init__(self):
        self.models_dir = settings.MODEL_DIR
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)

    def list_local_models(self) -> List[str]:
        """Mendaftar model yang sudah diunduh di direktori lokal."""
        return [d for d in os.listdir(self.models_dir) if os.path.isdir(os.path.join(self.models_dir, d))]

    def get_available_models(self) -> List[Dict[str, str]]:
        """Daftar model yang direkomendasikan untuk CodeAron."""
        return [
            {"name": "DeepSeek-Coder-V2-Lite-4bit", "id": "mlx-community/deepseek-coder-6.7b-instruct-4bit", "size": "~4.5GB"},
            {"name": "Llama-3-8B-Instruct-4bit", "id": "mlx-community/Meta-Llama-3-8B-Instruct-4bit", "size": "~5.5GB"},
            {"name": "Moondream2-Vision-4bit", "id": "mlx-community/moondream2-4bit", "size": "~1.5GB"}
        ]

    def display_hub(self):
        """Menampilkan tabel model yang tersedia dan statusnya."""
        table = Table(title="Aron Model Hub")
        table.add_column("Model Name", style="cyan")
        table.add_column("HuggingFace ID", style="magenta")
        table.add_column("Size", style="green")
        table.add_column("Status", style="yellow")

        local_models = self.list_local_models()
        available = self.get_available_models()

        for model in available:
            status = "✅ Terunduh" if model["id"].split('/')[-1] in local_models else "☁️ Tersedia"
            table.add_row(model["name"], model["id"], model["size"], status)

        console.print(table)
