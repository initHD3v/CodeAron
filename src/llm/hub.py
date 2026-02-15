from typing import List, Dict
import os
from src.core.config import settings
from rich.table import Table
from rich.console import Console
from huggingface_hub import snapshot_download
import questionary

console = Console()

class ModelHub:
    def __init__(self):
        self.models_dir = settings.MODEL_DIR
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)

    def list_local_models(self) -> List[str]:
        """Mendaftar model yang sudah diunduh di direktori lokal."""
        if not os.path.exists(self.models_dir): return []
        return [d for d in os.listdir(self.models_dir) if os.path.isdir(os.path.join(self.models_dir, d))]

    def get_available_models(self) -> List[Dict[str, str]]:
        """Daftar model yang direkomendasikan untuk CodeAron."""
        return [
            {"name": "DeepSeek-Coder-V2-Lite (4-bit)", "id": "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit-mlx", "size": "~10GB"},
            {"name": "Llama-3.1-8B-Instruct (4-bit)", "id": "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit", "size": "~5.5GB"},
            {"name": "Moondream2 (Vision) (4-bit)", "id": "mlx-community/moondream2-4bit", "size": "~1.5GB"}
        ]

    def download_model(self, model_id: str):
        """Mengunduh model dari Hugging Face ke folder lokal."""
        console.print(f"\n[bold cyan]Mengunduh model:[/bold cyan] {model_id}")
        console.print("[dim]Proses ini mungkin memakan waktu tergantung koneksi internet Anda...[/dim]\n")
        
        try:
            # Mengunduh model ke direktori yang dikonfigurasi
            repo_name = model_id.split("/")[-1]
            local_dir = self.models_dir / repo_name
            
            snapshot_download(
                repo_id=model_id,
                local_dir=local_dir,
                local_dir_use_symlinks=False
            )
            console.print(f"\n[bold green]✓ Berhasil![/bold green] Model disimpan di: {local_dir}")
        except Exception as e:
            console.print(f"\n[bold red]Gagal mengunduh model:[/bold red] {str(e)}")

    def display_hub(self):
        """Menampilkan tabel model dan memberikan opsi interaktif."""
        table = Table(title="Aron Model Hub")
        table.add_column("No", style="dim")
        table.add_column("Model Name", style="cyan")
        table.add_column("Size", style="green")
        table.add_column("Status", style="yellow")

        available = self.get_available_models()
        local_models = self.list_local_models()

        for i, model in enumerate(available, 1):
            repo_name = model["id"].split("/")[-1]
            status = "✅ Terunduh" if repo_name in local_models else "☁️ Tersedia"
            table.add_row(str(i), model["name"], model["size"], status)

        console.print(table)
        
        # Opsi interaktif setelah menampilkan tabel
        action = questionary.select(
            "Tindakan Model:",
            choices=["Download Model Baru", "Kembali ke Chat"]
        ).ask()
        
        if action == "Download Model Baru":
            model_to_download = questionary.select(
                "Pilih model untuk diunduh:",
                choices=[m["name"] for m in available]
            ).ask()
            
            selected_id = next(m["id"] for m in available if m["name"] == model_to_download)
            self.download_model(selected_id)
