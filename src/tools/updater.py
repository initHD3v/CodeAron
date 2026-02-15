import git
import os
import sys
import subprocess
from src.core.config import settings
from rich.console import Console

console = Console()

class AronUpdater:
    def __init__(self):
        try:
            self.repo = git.Repo(settings.BASE_DIR)
        except:
            self.repo = None

    def check_for_updates(self) -> bool:
        """Mengecek apakah ada commit baru di GitHub."""
        if not self.repo: return False
        try:
            # Fetch perubahan dari remote tanpa pull
            self.repo.remotes.origin.fetch()
            local_commit = self.repo.head.commit
            remote_commit = self.repo.remotes.origin.refs.main.commit
            return local_commit != remote_commit
        except:
            return False

    def perform_update(self):
        """Melakukan pull, reinstall, dan restart aplikasi."""
        if not self.repo:
            console.print("[bold red]Gagal:[/bold red] Repositori tidak ditemukan.")
            return

        try:
            with console.status("[bold green]Menarik kode terbaru dan menginstal dependensi...", spinner="dots"):
                self.repo.remotes.origin.pull()
                
                # Install dependensi dari requirements.txt
                req_path = os.path.join(settings.BASE_DIR, "requirements.txt")
                if os.path.exists(req_path):
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "-r", req_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )

                # Re-install untuk memastikan entry points diperbarui
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-e", str(settings.BASE_DIR)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            console.print("[bold green]✓ Update berhasil![/bold green] Memulai ulang CodeAron...")
            
            # Trik Hot-Restart: Mengganti proses saat ini dengan proses baru
            os.execv(sys.executable, [sys.executable] + sys.argv)
            
        except Exception as e:
            console.print(f"[bold red]Update gagal:[/bold red] {str(e)}")
