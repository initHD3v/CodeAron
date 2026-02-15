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
from rich.live import Live
import questionary
import time
import os
import difflib

from src.tools.updater import AronUpdater
from src.tools.patcher import CodePatcher
from src.tools.vision_engine import VisionEngine

console = Console()

class Orchestrator:
    def __init__(self):
        self.current_state: AronState = AronState.IDLE
        self.context: Dict[str, Any] = {}
        self.chat_history: List[Dict[str, str]] = [] # Memori percakapan
        self.retry_count: int = 0
        self.max_retries: int = settings.MAX_RETRIES if hasattr(settings, "MAX_RETRIES") else 3
        
        # Tools initialization
        self.inference = InferenceEngine()
        self.git = GitGuard(str(settings.CURRENT_PROJECT_DIR))
        self.bridge = FlutterBridge()
        self.hub = ModelHub()
        self.updater = AronUpdater()
        self.patcher = CodePatcher(str(settings.CURRENT_PROJECT_DIR))
        self.vision = VisionEngine()

    def transition_to(self, new_state: AronState):
        self.current_state = new_state

    def _extract_and_write_files(self, ai_response: str):
        """Mengekstrak blok kode <file path="..."> dan menuliskannya ke disk."""
        import re
        pattern = r'<file path="(.*?)">(.*?)</file>'
        matches = re.findall(pattern, ai_response, re.DOTALL)
        
        if matches:
            console.print("\n[bold cyan]🛠️  Aron menerapkan perubahan file...[/bold cyan]")
            for path, content in matches:
                console.print(f"  [dim]→ Menulis:[/dim] [green]{path}[/green]")
                self.patcher.write_full_file(path.strip(), content.strip())

    def interactive_session(self):
        available_commands = ["/quit", "/clear", "/model", "/update", "/reload"]
        
        while True:
            try:
                # Tampilkan info model dan directory
                model_display = os.path.basename(self.inference.model_path)
                project_display = str(settings.CURRENT_PROJECT_DIR).replace(os.path.expanduser("~"), "~")
                
                # Header info yang lebih minimalis
                console.print(f"\n[bold dim]╭─ AI: {model_display} | Proyek: {project_display}[/bold dim]")
                
                prompt = questionary.text("╰─❯", qmark="").ask()
                if prompt is None:
                    break
                
                cmd = prompt.strip()
                
                # Deteksi Typo untuk Perintah
                if cmd.startswith("/") and cmd not in available_commands:
                    matches = difflib.get_close_matches(cmd, available_commands, n=1, cutoff=0.6)
                    if matches:
                        suggestion = matches[0]
                        console.print(f"[yellow]  Mungkin maksud Anda: [bold]{suggestion}[/bold]?[/yellow]")
                        cmd = suggestion
                    else:
                        console.print(f"[red]  Perintah [bold]{cmd}[/bold] tidak dikenali.[/red]")
                        continue

                if cmd == "/quit":
                    console.print("[dim]  Sampai jumpa! 👋[/dim]")
                    break
                
                if cmd == "/clear":
                    self.chat_history = []
                    console.print("[bold yellow]  🧹 Memori percakapan telah dibersihkan.[/bold yellow]")
                    continue

                if cmd == "/model":
                    self.hub.display_hub()
                    continue
                
                if cmd == "/update":
                    self.updater.perform_update()
                    continue

                if cmd == "/reload":
                    console.print("[bold yellow]  🔄 Reloading CodeAron...[/bold yellow]")
                    import sys
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                    continue

                if cmd:
                    self.run_step(prompt)
            except KeyboardInterrupt:
                break

    def _get_history_context(self) -> str:
        """Mengambil beberapa pesan terakhir untuk memori."""
        context = ""
        for msg in self.chat_history[-6:]: 
            context += f"{msg['role']}: {msg['content']}\n"
        return context

    def _get_project_context(self) -> str:
        """Mengambil data nyata dari folder proyek secara dinamis."""
        try:
            files = []
            project_type = "Umum"
            
            for root, dirs, filenames in os.walk(settings.CURRENT_PROJECT_DIR):
                dirs[:] = [d for d in dirs if d not in ['.git', '.dart_tool', 'build', '.venv', 'node_modules', '__pycache__']]
                for f in filenames:
                    files.append(os.path.relpath(os.path.join(root, f), settings.CURRENT_PROJECT_DIR))
                    # Deteksi tipe proyek
                    if f == "pubspec.yaml": project_type = "Flutter/Dart"
                    elif f == "package.json": project_type = "Node.js/Web"
                    elif f == "requirements.txt" or f == "setup.py": project_type = "Python"
                    
                    if len(files) > 50: break
            
            context = f"Tipe Proyek Terdeteksi: {project_type}\n"
            context += f"Struktur File:\n{files[:30]}\n"
            
            # Tambahkan isi file penting jika ada
            important_files = ["pubspec.yaml", "package.json", "requirements.txt", "README.md"]
            for imp_file in important_files:
                path = os.path.join(settings.CURRENT_PROJECT_DIR, imp_file)
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        content = f.read(500)
                        context += f"\nIsi {imp_file}:\n{content}\n"
            
            return context
        except:
            return "Konteks proyek tidak tersedia."

    def run_step(self, user_input: str):
        """Alur logika dengan Streaming, Memory, dan Smart Context."""
        try:
            self.transition_to(AronState.INITIALIZING)
            
            # Deteksi Coding Intent (Optimasi Kecepatan)
            coding_keywords = ["buat", "tulis", "file", "code", "fungsi", "error", "dart", "flutter", "tambah", "ubah", "hapus", "proyek", "analisis", "tampilkan", "python", "fix"]
            is_coding_query = any(word in user_input.lower() for word in coding_keywords) or len(user_input) > 50
            
            project_info = ""
            if is_coding_query:
                with console.status("[bold cyan]Aron menganalisis proyek...", spinner="dots"):
                    project_info = self._get_project_context()
            
            history = self._get_history_context()
            
            system_prompt = (
                f"Kamu adalah CodeAron v{settings.VERSION}, asisten AI yang cerdas dan natural. "
                "Bicaralah seperti manusia. Gunakan Bahasa Indonesia.\n\n"
            )
            
            if project_info:
                system_prompt += f"DATA PROYEK (Referensi Utama):\n{project_info}\n\n"
            
            system_prompt += (
                "RIWAYAT PERCAKAPAN:\n"
                f"{history}\n"
                "TUGAS: Lanjutkan percakapan. Jika user hanya menyapa, balas dengan ramah dan singkat. "
                "Jika user bertanya teknis, gunakan data proyek untuk membantu. "
                "Gunakan format <file path=\"...\">isi</file> jika membuat file."
            )
            
            full_prompt = f"{system_prompt}\n\nUser: {user_input}\n\nAron:"
            
            self.transition_to(AronState.PLANNING)
            
            # UI Streaming
            console.print("\n[bold cyan]Aron:[/bold cyan]")
            full_response = ""
            
            with Live(Markdown(""), refresh_per_second=12, console=console) as live:
                for response in self.inference.generate_stream(full_prompt):
                    full_response += response
                    display_text = full_response.split("<|")[0].strip()
                    live.update(Markdown(display_text))
            
            clean_response = full_response.split("<|")[0].strip()
            
            # Simpan ke history
            self.chat_history.append({"role": "User", "content": user_input})
            self.chat_history.append({"role": "Aron", "content": clean_response})
            
            # Ekstrak file
            self._extract_and_write_files(clean_response)
            
            self.transition_to(AronState.IDLE)
            
        except Exception as e:
            console.print(f"\n[bold red]❌ Kesalahan:[/bold red] {str(e)}")
            self.transition_to(AronState.ERROR)
