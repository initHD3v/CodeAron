import os
import sys
import re
import subprocess
import gc
import logging
import signal
import time
from pathlib import Path
from typing import Dict, List, Optional

# UI & UX
import questionary
import psutil
from rich.console import Console, Group
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.table import Table
from rich.columns import Columns
from rich.progress import BarColumn, Progress, TextColumn
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

# System Config
from src.core.config import settings
from src.llm.inference import InferenceEngine
from src.tools.patcher import CodePatcher
from src.tools.validator import ValidationEngine
from src.memory.vector_store import VectorStore
from src.memory.indexer import ProjectIndexer
from src.llm.hub import ModelHub
from src.ui.renderer import UIRenderer, ARON_THEME

console = Console(theme=ARON_THEME)
logger = logging.getLogger("Orchestrator")

class Orchestrator:
    def __init__(self):
        self.chat_history: List[Dict[str, str]] = []
        self.process = psutil.Process(os.getpid())
        
        # Core Components
        self.inference = InferenceEngine() # Singleton
        self.patcher = CodePatcher(str(settings.CURRENT_PROJECT_DIR))
        self.validator = ValidationEngine(str(settings.CURRENT_PROJECT_DIR))
        self.hub = ModelHub()
        self.ui = UIRenderer()
        
        # Memory Components
        try:
            self.vector_store = VectorStore()
            self.indexer = ProjectIndexer(str(settings.CURRENT_PROJECT_DIR), vector_store=self.vector_store)
        except Exception as e:
            logger.warning(f"Semantic Memory disabled: {e}")
            self.vector_store = None
            self.indexer = None

        signal.signal(signal.SIGINT, self._signal_handler)

    def _get_resource_usage(self) -> Dict[str, float]:
        """Mengambil penggunaan CPU dan RAM aktual."""
        try:
            mem_info = self.process.memory_info()
            # RSS in GB
            ram_usage = mem_info.rss / (1024 ** 3)
            # CPU percent (interval=None for non-blocking)
            cpu_usage = self.process.cpu_percent(interval=None)
            return {"ram": ram_usage, "cpu": cpu_usage}
        except:
            return {"ram": 0.0, "cpu": 0.0}

    def _shutdown(self):
        console.print("[dim]Shutting down resources...[/dim]")
        if self.vector_store: self.vector_store.close()
        if self.inference: self.inference.unload_model()
        gc.collect()

    def _signal_handler(self, sig, frame):
        self._shutdown()
        sys.exit(0)

    def interactive_session(self):
        commands = {"/help": "Bantuan", "/clear": "Hapus History", "/flush": "Bebaskan RAM", "/quit": "Keluar"}
        
        def get_toolbar():
            stats = self._get_resource_usage()
            return HTML(self.ui.render_status_bar(stats['ram'], stats['cpu'], "Siap Membantu"))

        style = Style.from_dict({
            'bottom-toolbar': '#ffffff bg:#222222',
            'completion-menu.completion': 'bg:#008888 #ffffff',
            'completion-menu.completion.current': 'bg:#00aaaa #000000',
        })

        session = PromptSession(
            completer=WordCompleter(list(commands.keys()), ignore_case=True),
            bottom_toolbar=get_toolbar,
            style=style,
            refresh_interval=0.5
        )
        
        # Tampilkan Header Awal yang Fresh
        model_name = os.path.basename(self.inference.model_path) if self.inference.model_path else "None"
        console.print(self.ui.generate_header(settings.VERSION, model_name))
        
        while True:
            try:
                user_input = session.prompt(f"╭─❯ ")
                
                if not user_input.strip(): continue
                if user_input.startswith("/"):
                    cmd = user_input.split()[0].lower()
                    if cmd == "/quit": break
                    if cmd == "/flush": self.inference.unload_model(); continue
                    if cmd == "/clear": self.chat_history = []; console.clear(); console.print(self.ui.generate_header(settings.VERSION, model_name)); continue
                    if cmd == "/help":
                        console.print(Panel("\n".join([f"[bold cyan]{k}[/bold cyan]: {v}" for k,v in commands.items()]), title="Daftar Perintah", border_style="cyan"))
                        continue

                self.run_step(user_input)
            except (KeyboardInterrupt, EOFError): break
        self._shutdown()

    def run_step(self, user_input: str):
        try:
            rag_context = ""
            if self.vector_store:
                try:
                    results = self.vector_store.search(user_input, limit=2)
                    if results:
                        snippets = [f"File: {r.get('file_path')}\nCode:\n{r.get('content')[:500]}..." for r in results]
                        rag_context = "\n[CONTEXT FROM CODEBASE]\n" + "\n".join(snippets)
                except Exception as e:
                    logger.error(f"RAG failed: {e}")

            history_str = self._format_history(limit=3)
            # Protokol Instruksi Profesional & Anti-Halusinasi
            system_prompt = (
                "<｜begin of sentence｜>system\n"
                f"Identitas: Anda adalah Aron, Senior AI Software Architect. Lokasi Proyek: {os.getcwd()}\n"
                "\nPERINGATAN KERAS (ANTI-HALUSINASI):\n"
                "1. ANDA TUNA NETRA: Anda tidak bisa melihat struktur folder atau isi file apapun tanpa menggunakan <shell>. DILARANG KERAS berasumsi atau mengarang isi file.\n"
                "2. EKSEKUSI MANDATORY: Jika user minta analisa, langkah pertama WAJIB <shell>ls -R</shell>. Langkah kedua WAJIB <shell>cat <file></shell>.\n"
                "3. STOP IMMEDIATELY: Setelah menulis </shell> atau </file>, Anda harus segera berhenti. Jangan memprediksi output.\n"
                "4. DILARANG menggunakan format <｜tool...｜>. Gunakan hanya format <shell> atau <file>.\n"
                "5. GAYA KOMUNIKASI: Profesional, teknis, dan berbasis data empiris.\n"
                "\nSTRUKTUR RESPONS:\n"
                "   - Ringkasan Eksekutif (Hanya setelah data ada)\n"
                "   - Analisis Tech Stack (Berdasarkan requirements/setup.py)\n"
                "   - Pemetaan Arsitektur (Berdasarkan konten src/)\n"
                f"{rag_context}\n"
                f"{history_str}\n"
                f"User: {user_input}\n"
                "Assistant:"
            )

            full_response = ""
            with Live(console=console, refresh_per_second=4) as live:
                # Gunakan temperatur rendah (0.2) untuk akurasi teknis
                for chunk in self.inference.generate_stream(
                    system_prompt, 
                    max_tokens=settings.MAX_TOKENS_GEN,
                    temp=0.2,
                    stop_sequences=["User:", "Assistant:", "Aron:", "</shell>", "</file>", "<｜", "```"]
                ):
                    full_response += chunk
                    
                    # Bersihkan teks untuk display
                    display_text = re.sub(r'<\|.*?\|>', '', full_response)
                    
                    # Update Tampilan Live
                    stats = self._get_resource_usage()
                    status_line = self.ui.render_live_status(stats['ram'], stats['cpu'])
                    
                    live.update(Group(
                        self.ui.render_message("User", user_input),
                        self.ui.render_message("Aron", display_text),
                        status_line
                    ))

            self._handle_actions(full_response)
            self.chat_history.append({"role": "User", "content": user_input})
            self.chat_history.append({"role": "Aron", "content": full_response[:2000]})

        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {e}")

    def _format_history(self, limit: int = 3) -> str:
        out = []
        for msg in self.chat_history[-limit*2:]:
            content = re.sub(r'<file.*?>.*?</file>', '[FILE WRITTEN]', msg['content'], flags=re.DOTALL)
            out.append(f"{msg['role']}: {content}")
        return "\n".join(out)

    def _handle_actions(self, response: str):
        # Regex yang lebih toleran terhadap tag penutup yang mungkin terpotong
        files = re.findall(r'<file\s+path=[\'"](.*?)[\'"]>(.*?)(?:</file>|$)', response, re.DOTALL | re.IGNORECASE)
        for path, content in files:
            if content.strip() and questionary.confirm(f"Write to {path.strip()}?", default=True).ask():
                self.patch_file(path.strip(), content.strip())

        shells = re.findall(r'<shell>(.*?)(?:</shell>|$)', response, re.DOTALL | re.IGNORECASE)
        for cmd in shells:
            if cmd.strip() and questionary.confirm(f"Run: {cmd.strip()}?", default=True).ask():
                try: subprocess.run(cmd.strip(), shell=True, check=True)
                except: console.print("[red]Command failed.[/red]")

    def patch_file(self, path: str, content: str):
        """Memanggil patcher untuk menulis file."""
        try:
            self.patcher.write_full_file(path, content)
            console.print(f"[bold green]Berhasil menulis ke {path}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Gagal menulis ke {path}: {e}[/bold red]")
