from typing import Optional, Dict, Any
from .states import AronState
from .config import settings
from src.llm.inference import InferenceEngine
from src.tools.git_guard import GitGuard
from src.tools.flutter_bridge import FlutterBridge
from src.llm.hub import ModelHub
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import questionary
import time
import os

from src.tools.updater import AronUpdater

console = Console()

class Orchestrator:
    def __init__(self):
        self.current_state: AronState = AronState.IDLE
        self.context: Dict[str, Any] = {}
        self.retry_count: int = 0
        self.max_retries: int = settings.MAX_RETRIES if hasattr(settings, "MAX_RETRIES") else 3
        
        # Tools initialization
        self.inference = InferenceEngine()
        self.git = GitGuard(str(settings.CURRENT_PROJECT_DIR))
        self.bridge = FlutterBridge()
        self.hub = ModelHub()
        self.updater = AronUpdater()

    def transition_to(self, new_state: AronState):
        self.current_state = new_state

    def interactive_session(self):
        while True:
            try:
                prompt = questionary.text("❯", qmark="").ask()
                if prompt is None or prompt.strip() == "/quit":
                    console.print("[dim]Sampai jumpa! 👋[/dim]")
                    break
                
                cmd = prompt.strip()
                if cmd == "/model":
                    self.hub.display_hub()
                    continue
                
                if cmd == "/update":
                    self.updater.perform_update()
                    continue

                if cmd == "/reload":
                    console.print("[bold yellow]🔄 Reloading CodeAron dari kode lokal...[/bold yellow]")
                    import sys
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                    continue

                self.run_step(prompt)
            except KeyboardInterrupt:
                break

    def _get_project_context(self) -> str:
        """Mengambil data nyata dari folder proyek untuk diberikan ke AI."""
        try:
            files = []
            for root, dirs, filenames in os.walk(settings.CURRENT_PROJECT_DIR):
                # Abaikan folder yang tidak perlu
                dirs[:] = [d for d in dirs if d not in ['.git', '.dart_tool', 'build', '.venv', 'node_modules']]
                for f in filenames:
                    files.append(os.path.relpath(os.path.join(root, f), settings.CURRENT_PROJECT_DIR))
                    if len(files) > 50: break # Batasi agar context tidak penuh
            
            # Coba baca pubspec.yaml
            pubspec_content = ""
            pubspec_path = os.path.join(settings.CURRENT_PROJECT_DIR, "pubspec.yaml")
            if os.path.exists(pubspec_path):
                with open(pubspec_path, 'r') as f:
                    pubspec_content = f.read()

            return f"Struktur File:\n{files[:30]}\n\nIsi pubspec.yaml:\n{pubspec_content[:1000]}"
        except:
            return "Gagal membaca konteks proyek."

    def run_step(self, user_input: str):
        """Alur logika dengan Konteks Nyata."""
        try:
            self.transition_to(AronState.INITIALIZING)
            
            with console.status("[bold cyan]Aron sedang menganalisis proyek...", spinner="dots"):
                self.transition_to(AronState.PLANNING)
                
                project_info = self._get_project_context()
                model_name = os.path.basename(self.inference.model_path)
                
                system_prompt = (
                    f"Kamu adalah CodeAron v{settings.VERSION}, asisten coding lokal yang cerdas. "
                    "Tugasmu adalah menganalisis proyek user berdasarkan data nyata yang diberikan. "
                    "JANGAN menggunakan format internal function calling seperti <|tool|>. "
                    "JANGAN berhalusinasi tentang nama proyek. Gunakan data yang ada di bawah ini.\n\n"
                    f"DATA PROYEK SAAT INI:\n{project_info}\n\n"
                    "Berikan jawaban dalam Bahasa Indonesia yang profesional dengan format Markdown."
                )
                
                full_prompt = f"{system_prompt}\n\nUser: {user_input}\n\nAron:"
                response = self.inference.generate(full_prompt)
                
            # Bersihkan sisa-sisa tag jika model masih bandel
            clean_response = response.replace("<|tool▁calls▁begin|>", "").replace("<|tool▁call▁begin|>", "").split("<|")[0]
            
            console.print("\n" + "─" * console.width)
            console.print(Markdown(clean_response.strip()))
            console.print("─" * console.width + "\n")
            
            self.transition_to(AronState.IDLE)
            
        except Exception as e:
            console.log(f"[bold red]Error Fatal:[/bold red] {str(e)}")
            self.transition_to(AronState.ERROR)
