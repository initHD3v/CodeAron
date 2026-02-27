import os
import sys
import re
import subprocess
import gc
import logging
import signal
import time
import hashlib
import select
import tty
import termios
import json
import shlex
from collections import deque, Counter
from typing import Dict, List, Optional

# UI & UX
import questionary
import psutil
from rich.console import Console, Group
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings

# System Config
from src.core.config import settings
from src.core.states import AronState, ExecutionResult
from src.core.prompt_templates import PromptTemplateManager, ModelFamily
from src.llm.inference import InferenceEngine
from src.tools.patcher import CodePatcher
from src.tools.validator import ValidationEngine
from src.memory.vector_store import VectorStore
from src.memory.indexer import ProjectIndexer
from src.llm.hub import ModelHub
from src.ui.renderer import UIRenderer, ARON_THEME
from src.tools.git_guard import GitGuard
from src.tools.vision_engine import VisionEngine

# Cognitive Modules
from src.core.planner import TaskPlanner
from src.core.router import ToolRouter
from src.core.critic import SelfCritic
from src.core.confidence import ConfidenceEngine
from src.core.metrics import MetricsTracker
from src.core.memory import MemoryManager, ContextCompressor
from src.core.recovery import RecoveryEngine

console = Console(theme=ARON_THEME)
logger = logging.getLogger("Orchestrator")

# Perintah yang aman untuk auto-execute tanpa konfirmasi (harus diperiksa lebih lanjut)
AUTO_CONFIRM_BASE = ["ls", "pwd", "head", "tail", "find", "grep", "which", "echo", "cat", "wc", "tree"]
# Catatan: cat sekarang auto-confirm karena read-only

# Perintah interaktif yang tidak didukung
INTERACTIVE_COMMANDS = ["vim", "nano", "git commit", "apt", "npm init", "cpan"]

class Orchestrator:
    def __init__(self):
        self.chat_history: List[Dict[str, str]] = []
        self.process = psutil.Process(os.getpid())
        self.state = AronState.IDLE
        self._last_stats = {"ram": 0.0, "cpu": 0.0}
        self._last_update_time = 0.0
        self.command_history = deque(maxlen=5)  # untuk deteksi osilasi (simpan tuple)
        self.cwd = os.getcwd()  # Lacak direktori kerja saat ini
        
        # Rate limiting untuk shell commands
        self._last_command_time = 0.0
        self._command_cooldown = 2.0  # 2 detik antar perintah
        self._consecutive_failures = 0
        self._max_consecutive_failures = 5  # Circuit breaker threshold

        self.inference = InferenceEngine()
        self.patcher = CodePatcher(str(settings.CURRENT_PROJECT_DIR))
        self.validator = ValidationEngine(str(settings.CURRENT_PROJECT_DIR))
        self.ui = UIRenderer()
        self.git = GitGuard(str(settings.CURRENT_PROJECT_DIR))
        self.vision = VisionEngine()
        
        try:
            self.vector_store = VectorStore()
        except Exception as e:
            logger.error(f"VectorStore init failed: {e}")
            self.vector_store = None
        
        self.planner = TaskPlanner()
        self.router = ToolRouter()
        self.critic = SelfCritic()
        self.confidence_engine = ConfidenceEngine()
        self.metrics = MetricsTracker()
        self.memory = MemoryManager(vector_store=self.vector_store)
        self.compressor = ContextCompressor()
        
        self.memory.load_project_memory()
        
        signal.signal(signal.SIGINT, self._signal_handler)

    def _get_resource_usage(self) -> Dict[str, float]:
        """Get resource usage dengan copy dictionary untuk mencegah memory leak."""
        now = time.time()
        if now - self._last_update_time > 3.0:
            try:
                mem_info = self.process.memory_info()
                self._last_stats = {
                    "ram": mem_info.rss / (1024 ** 3),
                    "cpu": psutil.cpu_percent()
                }
                self._last_update_time = now
            except Exception as e:
                logger.debug(f"Resource usage check failed: {e}")
                pass
        return self._last_stats.copy()  # Return copy untuk mencegah reference leak

    def _shutdown(self):
        console.print("\n[dim]Menutup sesi CodeAron secara aman...[/dim]")
        try:
            if hasattr(self, 'vector_store') and self.vector_store:
                self.vector_store.close()
        except Exception:
            pass
        try:
            if hasattr(self, 'inference') and self.inference:
                self.inference.unload_model()
        except Exception:
            pass
        console.print(self.ui.render_shutdown_summary(self.chat_history))
        sys.stdout.flush()
        # Gunakan sys.exit, bukan os._exit, agar lebih graceful
        sys.exit(0)

    def _signal_handler(self, sig, frame):
        self._shutdown()

    def interactive_session(self):
        if self.vector_store and self.vector_store.count_points() == 0:
            indexer = ProjectIndexer(str(settings.CURRENT_PROJECT_DIR), self.vector_store)
            indexer.scan_project()

        commands = ["/help", "/clear", "/hub", "/update", "/undo", "/checkpoint", "/quit", "@"]
        
        # Custom completion untuk gambar DAN commands
        import glob
        from prompt_toolkit.completion import Completer, Completion
        from prompt_toolkit.filters import Condition
        
        class AronCompleter(Completer):
            def __init__(self, cwd):
                self.cwd = cwd
                self.image_extensions = ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp", "*.bmp", "*.svg"]
                self.commands = {
                    "/help": "Tampilkan bantuan",
                    "/clear": "Bersihkan layar",
                    "/hub": "Kelola model AI",
                    "/update": "Update CodeAron",
                    "/undo": "Rollback perubahan",
                    "/checkpoint": "Git commit",
                    "/quit": "Keluar",
                    "/vision": "Analisis gambar",
                }
            
            def get_completions(self, document, complete_event):
                text = document.text_before_cursor
                
                # Completion untuk @ (images) - popup saat ketik @
                if text == '@' or text.startswith('@'):
                    image_files = []
                    for ext in self.image_extensions:
                        image_files.extend(glob.glob(os.path.join(self.cwd, ext)))
                        image_files.extend(glob.glob(os.path.join(self.cwd, ext.upper())))
                    
                    word_after_at = text[1:] if len(text) > 1 else ""
                    
                    for img_path in sorted(image_files):
                        img_name = os.path.basename(img_path)
                        if word_after_at == "" or img_name.lower().startswith(word_after_at.lower()):
                            file_size = os.path.getsize(img_path) / 1024
                            yield Completion(
                                img_name,
                                start_position=-len(word_after_at),
                                display=f"📷 {img_name} ({file_size:.1f} KB)",
                                style="fg:cyan"
                            )
                
                # Completion untuk / (commands) - popup saat ketik /
                elif text == '/' or text.startswith('/'):
                    word = text
                    
                    for cmd, desc in sorted(self.commands.items()):
                        if cmd.lower().startswith(word.lower()):
                            yield Completion(
                                cmd,
                                start_position=-len(word),
                                display=HTML(f'<style fg="green">⚡ {cmd}</style> <style fg="gray">{desc}</style>'),
                                style="fg:green"
                            )
        
        session = PromptSession(
            completer=AronCompleter(self.cwd),
            complete_while_typing=Condition(lambda: True),
            bottom_toolbar=lambda: HTML(self.ui.render_status_bar(
                self._get_resource_usage()['ram'],
                self._get_resource_usage()['cpu'],
                self.state.value,
                self.vector_store.count_points() if self.vector_store else 0
            )),
            style=Style.from_dict({
                'bottom-toolbar': '#ffffff bg:#1a1a1a',
                'completion-menu.completion': 'bg:#1a1a1a #ffffff',
                'completion-menu.completion.current': 'bg:#00aaaa #ffffff',
            }),
            refresh_interval=2.0
        )

        console.clear()
        console.print(self.ui.generate_header(settings.VERSION, os.path.basename(self.inference.model_path)))

        while True:
            try:
                user_input = session.prompt(f"╭─❯ ")
                if not user_input.strip():
                    continue
                
                # Check untuk / command tanpa argumen
                if user_input.strip() == "/":
                    console.print("[dim]  (Ketik /help, /clear, dll. atau backspace untuk cancel)[/dim]")
                    continue
                
                # Check for @ trigger untuk image analysis
                if user_input.strip() == "@" or user_input.strip().startswith("@ "):
                    # Jika hanya @ tanpa filename, abaikan dan lanjut chat
                    if user_input.strip() == "@":
                        console.print("[dim]  (Ketik @filename.png untuk analyze gambar, atau backspace untuk cancel)[/dim]")
                        continue
                    
                    # Extract filename jika ada
                    parts = user_input.strip().split(" ", 1)
                    if len(parts) > 1 and parts[1].strip():
                        # User sudah pilih file dari completion
                        filename = parts[1].strip()
                        selected_path = os.path.join(self.cwd, filename)
                        
                        if os.path.exists(selected_path):
                            console.print(f"\n[dim]Menganalisis {filename}...[/dim]")
                            try:
                                result = self.vision.analyze_image(selected_path, "Deskripsikan gambar ini untuk developer.")
                                console.print(Panel(result, title=f"Vision Analysis: {filename}", border_style="cyan"))
                            except Exception as e:
                                console.print(f"[bold red]Error:[/bold red] {e}")
                        else:
                            console.print(f"[yellow]File tidak ditemukan: {filename}[/yellow]")
                        continue
                    
                    # Fallback ke list manual jika tidak ada file dipilih
                    import glob
                    image_extensions = ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp", "*.bmp", "*.svg"]
                    image_files = []
                    
                    for ext in image_extensions:
                        image_files.extend(glob.glob(os.path.join(self.cwd, ext), recursive=False))
                        image_files.extend(glob.glob(os.path.join(self.cwd, ext.upper()), recursive=False))
                    
                    if not image_files:
                        console.print("[yellow]⚠ Tidak ada file gambar di direktori ini.[/yellow]")
                        console.print("[dim]  Supported: PNG, JPG, GIF, WEBP, BMP, SVG[/dim]")
                        continue
                    
                    # Display image files
                    console.print("\n[bold cyan]📷 Pilih gambar untuk dianalisis:[/bold cyan]")
                    for idx, img_path in enumerate(sorted(image_files), 1):
                        img_name = os.path.basename(img_path)
                        file_size = os.path.getsize(img_path) / 1024
                        console.print(f"  [dim]{idx}.[/dim] [cyan]{img_name}[/cyan] [dim]({file_size:.1f} KB)[/dim]")
                    
                    # Get user selection
                    try:
                        selection = questionary.select(
                            "Pilih gambar (ESC to cancel):",
                            choices=[os.path.basename(f) for f in sorted(image_files)] + ["❌ Cancel"]
                        ).ask()
                        
                        if not selection or selection == "❌ Cancel":
                            console.print("[dim]  Cancelled.[/dim]")
                            continue
                        
                        selected_path = None
                        for f in sorted(image_files):
                            if os.path.basename(f) == selection:
                                selected_path = f
                                break
                        
                        if selected_path:
                            console.print(f"\n[dim]Menganalisis {selection}...[/dim]")
                            try:
                                result = self.vision.analyze_image(selected_path, "Deskripsikan gambar ini untuk developer.")
                                console.print(Panel(result, title=f"Vision Analysis: {selection}", border_style="cyan"))
                            except Exception as e:
                                console.print(f"[bold red]Error:[/bold red] {e}")
                    
                    except KeyboardInterrupt:
                        console.print("[dim]  Cancelled.[/dim]")
                        continue
                    
                    continue
                
                if user_input == "/quit":
                    break
                if user_input == "/clear":
                    self.chat_history = []
                    console.clear()
                    console.print(self.ui.generate_header(settings.VERSION, os.path.basename(self.inference.model_path)))
                    continue
                if user_input == "/undo":
                    if questionary.confirm("Batalkan perubahan terakhir?").ask():
                        self.git.rollback()
                        console.print("[bold green]✓ Berhasil Rollback.[/bold green]")
                    continue
                if user_input == "/checkpoint":
                    try:
                        msg = questionary.text("Pesan commit (ESC to cancel):").ask()
                        if not msg or msg.strip() == "":
                            console.print("[dim]  Commit cancelled.[/dim]")
                            continue
                        self.git.commit_changes(msg)
                        console.print(f"[bold green]✓ Checkpoint '{msg}' dibuat.[/bold green]")
                    except KeyboardInterrupt:
                        console.print("[dim]  Commit cancelled.[/dim]")
                    continue
                if user_input == "/hub":
                    ModelHub().display_hub()
                    continue
                if user_input == "/help":
                    self.ui.render_help()
                    continue
                if user_input == "/update":
                    from src.tools.updater import AronUpdater
                    updater = AronUpdater()
                    
                    # Check dulu apakah ada update
                    console.print("[dim]Memeriksa update...[/dim]")
                    if updater.check_for_updates():
                        console.print("[bold green]✓ Update tersedia![/bold green]")
                        updater.perform_update()
                    else:
                        console.print("[bold green]✓ Anda menggunakan versi terbaru![/bold green]")
                    continue
                if user_input.startswith("/vision"):
                    # Handle vision command for image analysis
                    parts = user_input.split(" ", 1)
                    if len(parts) > 1 and parts[1].strip():
                        image_path = parts[1].strip()
                        prompt = "Deskripsikan gambar ini untuk developer."
                    else:
                        # Custom input dengan ESC handling
                        console.print("[dim]Path ke gambar (ESC to cancel):[/dim]", end=" ")
                        try:
                            import select, tty, termios, sys
                            
                            # Save terminal settings
                            fd = sys.stdin.fileno()
                            old_settings = termios.tcgetattr(fd)
                            
                            try:
                                tty.setraw(fd)
                                chars = []
                                
                                while True:
                                    ch = sys.stdin.read(1)
                                    if ch == '\x1b':  # ESC
                                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                                        console.print("\r[dim]  Vision cancelled.[/dim]")
                                        console.print()  # New line
                                        break
                                    elif ch == '\r' or ch == '\n':  # Enter
                                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                                        console.print()  # New line
                                        break
                                    elif ch == '\x7f' or ch == '\b':  # Backspace
                                        if chars:
                                            chars.pop()
                                            console.print("\b \b", end="")
                                    else:
                                        chars.append(ch)
                                        console.print(ch, end="")
                                
                                # Restore settings
                                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                                
                                image_path = ''.join(chars).strip()
                                if not image_path:
                                    continue
                                
                                # Optional prompt
                                console.print("[dim]Pertanyaan (ESC to skip):[/dim]", end=" ")
                                chars = []
                                old_settings = termios.tcgetattr(fd)
                                try:
                                    tty.setraw(fd)
                                    while True:
                                        ch = sys.stdin.read(1)
                                        if ch == '\x1b':  # ESC
                                            prompt = "Deskripsikan gambar ini untuk developer."
                                            break
                                        elif ch == '\r' or ch == '\n':
                                            break
                                        elif ch == '\x7f' or ch == '\b':
                                            if chars:
                                                chars.pop()
                                                console.print("\b \b", end="")
                                        else:
                                            chars.append(ch)
                                            console.print(ch, end="")
                                    prompt = ''.join(chars).strip() or "Deskripsikan gambar ini untuk developer."
                                finally:
                                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                                console.print()
                                
                            except Exception as e:
                                # Fallback to questionary jika custom input gagal
                                image_path = questionary.text("Path ke gambar:").ask()
                                if not image_path:
                                    continue
                                prompt = questionary.text("Pertanyaan (opsional):", 
                                                        default="Deskripsikan gambar ini untuk developer.").ask()
                                if prompt is None:
                                    prompt = "Deskripsikan gambar ini untuk developer."
                                    
                        except KeyboardInterrupt:
                            console.print("\r[dim]  Vision cancelled.[/dim]")
                            console.print()
                            continue

                    try:
                        result = self.vision.analyze_image(image_path.strip(), prompt)
                        console.print(Panel(result, title="Vision Analysis", border_style="cyan"))
                    except Exception as e:
                        console.print(f"[bold red]Error:[/bold red] {e}")
                    continue
                self.run_cycle(user_input)
            except (KeyboardInterrupt, EOFError):
                break
        self._shutdown()

    def run_cycle(self, initial_input: str):
        """
        Main execution cycle dengan fast path untuk command sederhana.
        """
        self.metrics.start_request()

        # === FAST PATH: Direct responses ===
        
        # 1. Greeting - langsung response tanpa analysis
        greetings = ["hai", "halo", "hi", "p", "siapa ini", "pagi", "siang", "sore", "malam"]
        if initial_input.lower().strip() in greetings:
            response = "Halo! Saya Aron. Ada yang bisa saya bantu?"
            self.chat_history.append({"role": "User", "content": initial_input})
            self.chat_history.append({"role": "Aron", "content": response})
            console.print(self.ui.render_message("Aron", response))
            return response
        
        # 2. Simple shell commands - langsung execute tanpa multi-turn
        simple_patterns = [r"^ls\s", r"^ls$", r"^pwd$", r"^head\s", r"^tail\s", r"^cat\s", r"^grep\s", r"^which\s", r"^echo\s"]
        is_simple_shell = any(re.match(pattern, initial_input.strip()) for pattern in simple_patterns)
        
        if is_simple_shell:
            cmd = initial_input.strip()
            # Smart filtering untuk ls -R
            if cmd == "ls -R" or cmd == "ls":
                # Gunakan find untuk skip directory yang tidak perlu
                cmd = "find . -maxdepth 3 -type f -not -path '*/\\.*' -not -path '*/__pycache__/*' -not -path '*/.venv/*' -not -path '*/venv/*' -not -path '*/node_modules/*' | head -50"
            
            result = self._run_shell(cmd)
            if result.success:
                output = result.output if result.output.strip() else "(tidak ada output)"
                if len(output) > 3000:
                    output = output[:1500] + "\n... [truncated] ...\n" + output[-1500:]
                console.print(Panel(output, title=f"Output: {initial_input.strip()}", border_style="green"))
                self.chat_history.append({"role": "User", "content": initial_input})
                self.chat_history.append({"role": "Aron", "content": f"Executed: {initial_input.strip()}"})
                return output
            else:
                console.print(f"[red]Error: {result.error}[/red]")
                return result.error
        
        # === SLOW PATH: Cognitive loop untuk task kompleks ===
        
        self.state = AronState.ANALYZING
        depth: int = 0
        current_input: str = initial_input
        refinement_count: int = 0
        max_refinement: int = 2  # Reduced from 5 to 2 for faster response
        critic_feedback = None
        clean_response = ""
        action_results = []
        last_commands_tuple = ()

        # Deteksi task complexity untuk adjust max_refinement
        complex_keywords = ["refactor", "architect", "design", "review", "optimize", "restructure"]
        if any(keyword in initial_input.lower() for keyword in complex_keywords):
            max_refinement = 3  # More iterations for complex tasks
        else:
            max_refinement = 1  # Single pass for most tasks

        while depth < 3:  # Reduced from 5 to 3 max iterations
            try:
                self.state = AronState.PLANNING
                raw_context = self.memory.get_combined_context(current_input)
                comp_context = self.compressor.compress(raw_context)
                
                task_plan = self.planner.create_plan(current_input, comp_context)
                # Task complexity hidden
                # for step in task_plan.steps:
                    #     console.print(f"  └ {step}")
                
                self.state = AronState.ROUTING
                routing_info = self.router.route(current_input, comp_context)
                # Tool suggestion hidden

                self.state = AronState.EXECUTING
                prompt = self._build_prompt(current_input, comp_context)
                full_response = ""
                
                old_settings = termios.tcgetattr(sys.stdin)
                try:
                    termios.tcflush(sys.stdin, termios.TCIFLUSH)
                    tty.setcbreak(sys.stdin.fileno())
                    with Live(console=console, refresh_per_second=4) as live:
                        for chunk in self.inference.generate_stream(
                            prompt, temp=0.1,
                            stop_sequences=["<|im_start|>", "<|im_end|>", "User:", "Assistant:"]
                        ):
                            full_response += chunk
                            live.update(Group(
                                self.ui.render_message("Aron", full_response),
                                self.ui.render_live_status(
                                    self._get_resource_usage()['ram'],
                                    self._get_resource_usage()['cpu']
                                )
                            ))
                            if select.select([sys.stdin], [], [], 0)[0]:
                                if sys.stdin.read(1) == '\x1b':
                                    break
                finally:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

                # Proses aksi (shell dan file)
                action_results = self._process_actions(full_response)
                
                # Ekstrak perintah yang berhasil untuk deteksi loop
                executed_commands = []
                for res in action_results:
                    match = re.search(r"(?:Output perintah|Perintah) '([^']+)'", res)
                    if match and "GAGAL" not in res:
                        executed_commands.append(match.group(1))
                
                # Deteksi loop sederhana (satu langkah)
                current_tuple = tuple(executed_commands)
                if current_tuple and current_tuple == last_commands_tuple:
                    console.print("[yellow]⚠ Model mengulang perintah yang sama. Hentikan siklus.[/yellow]")
                    break
                last_commands_tuple = current_tuple

                # Deteksi osilasi (beberapa langkah)
                if executed_commands:
                    self.command_history.append(current_tuple)
                    freq = Counter(self.command_history)
                    if any(count >= 3 for count in freq.values()):
                        console.print("[yellow]⚠ Terdeteksi osilasi perintah. Hentikan siklus.[/yellow]")
                        break

                # Jika ada hasil eksekusi, tampilkan dan masukkan ke konteks
                if action_results:
                    output_text = "\n".join(action_results)
                    console.print(Panel(output_text, title="Output Perintah", border_style="green"))
                    # Tambahkan ke memory sebagai pesan system (agar model tidak bingung)
                    self.memory.add_short_term("system", f"[ENVIRONMENT] Output:\n{output_text}")
                    self.chat_history.append({"role": "system", "content": f"Output:\n{output_text}"})
                    # Gunakan output sebagai input untuk putaran berikutnya
                    current_input = output_text
                else:
                    # Jika tidak ada aksi, hentikan siklus
                    break

                self.state = AronState.CRITIQUING
                critic_feedback = self.critic.evaluate(current_input, full_response)
                
                if critic_feedback.flaws:
                    console.print(f"[bold yellow]⚠ Critic Insight:[/bold yellow]")
                    for flaw in critic_feedback.flaws:
                        console.print(f"  [yellow]- {flaw}[/yellow]")

                if self.critic.needs_refinement(critic_feedback) and refinement_count < max_refinement:
                    self.state = AronState.REFINING
                    refinement_count += 1
                    current_input = f"[CRITIC FEEDBACK]: {json.dumps(critic_feedback.flaws)}\nPlease correct the above issues."
                    continue

                self.state = AronState.VERIFYING
                clean_response = re.sub(r'^(Aron|Assistant|User|\[RESPONSE\]):\s*', '', full_response, flags=re.MULTILINE | re.IGNORECASE).strip()
                
                # Tambahkan respons Aron ke memory
                self.memory.add_short_term("Aron", clean_response)
                self.chat_history.append({"role": "Aron", "content": clean_response})
                
                depth += 1
                # console.print(f"\n[dim italic] ● Berpikir... (Putaran {int(depth)}/5)[/dim italic]")

            except Exception as e:
                logger.error(f"Cycle failed: {e}")
                console.print(f"[red]Terjadi kesalahan internal: {e}[/red]")
                self.state = AronState.FAILED
                break

        if critic_feedback is None:
            critic_feedback = self.critic.evaluate(initial_input, clean_response or "")
        conf_score = self.confidence_engine.calculate_score(
            critic_severity=critic_feedback.severity_score,
            tool_success=bool(action_results),
            retry_count=refinement_count
        )
        console.print(f"[dim]● Final Confidence: [bold]{conf_score:.2f}[/bold][/dim]")
        
        self.state = AronState.IDLE
        return self.confidence_engine.wrap_response(clean_response, {
            "confidence": conf_score,
            "tools_used": ["shell"] if action_results else ["none"],
            "iterations": depth + 1,
            "model": "qwen2.5-coder"
        })

    def _sanitize_history(self) -> List[Dict[str, str]]:
        clean_history = []
        for m in self.chat_history:
            content = re.sub(r'^(Aron|User|Assistant|\[THOUGHTS\]|\[STRATEGY\]|\[SOLUTION\]|\[RESPONSE\]):\s*', '', m['content'], flags=re.MULTILINE | re.IGNORECASE)
            if content.strip():
                clean_history.append({"role": m['role'], "content": content.strip()})
        return clean_history[-10:]

    def _build_prompt(self, user_input: str, rag_context: str) -> str:
        history = self._sanitize_history()
        
        # Deteksi model untuk fallback template
        model_name = os.path.basename(self.inference.model_path).lower()
        
        system_rules = (
            "You are Aron, a Senior AI Architect running LOCALLY on Apple Silicon.\n"
            "Current directory: {cwd}\n\n"
            "MANDATORY RULES:\n"
            "1. For 'analisa' or 'analyze' requests: FIRST read README.md or main files, THEN provide structured analysis.\n"
            "2. Use <shell>command</shell> for terminal actions.\n"
            "3. Use <file path=\"...\">content</file> for file writing.\n"
            "4. NO Markdown blocks (```). Just execute.\n"
            "5. ALWAYS verify file exists before cat: use 'ls filename' or 'test -f filename' first.\n"
            "6. If command fails, acknowledge error and try alternative approach.\n"
            "7. After gathering info, provide SUMMARY with: Project Type, Structure, Key Files, Recommendations.\n"
            "8. Keep responses concise and actionable.\n"
            "9. Avoid interactive commands like vim, nano, etc.\n"
            "10. For directory listing, use 'find' command to skip .venv, __pycache__, node_modules.\n\n"
            "EXAMPLE ANALYSIS FLOW:\n"
            "User: analisa project ini\n"
            "Assistant: <shell>cat README.md</shell>\n"
            "User: [README content]\n"
            "Assistant: <shell>ls *.py</shell>\n"
            "User: [file list]\n"
            "Assistant: ## Analisis Project\n\n**Type:** Python App\n**Structure:** [summary]\n**Key Files:** [list]\n**Recommendations:** [suggestions]\n"
        ).format(cwd=self.cwd)  # Gunakan self.cwd yang dilacak

        messages = [{"role": "system", "content": system_rules}]
        for m in history:
            # Ubah peran "system" menjadi "user" untuk output? Tidak, kita sudah simpan sebagai system
            # Tapi model mungkin tidak mendukung banyak system messages. Alternatif: tetap kirim sebagai user dengan prefix.
            # Kita akan kirim sebagai user dengan label [ENVIRONMENT] agar jelas.
            if m['role'] == 'system':
                # Bungkus dalam user message dengan prefix
                messages.append({"role": "user", "content": f"[ENVIRONMENT]\n{m['content']}"})
            else:
                messages.append({"role": m['role'].lower(), "content": m['content']})
        messages.append({"role": "user", "content": user_input})
        
        try:
            return self.inference.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        except Exception:
            # Fallback berdasarkan model
            if "llama" in model_name:
                # Format Llama 3
                prompt = "<|begin_of_text|>"
                for msg in messages:
                    if msg['role'] == 'system':
                        prompt += f"<|start_header_id|>system<|end_header_id|>\n\n{msg['content']}<|eot_id|>"
                    elif msg['role'] == 'user':
                        prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{msg['content']}<|eot_id|>"
                    else:
                        prompt += f"<|start_header_id|>assistant<|end_header_id|>\n\n{msg['content']}<|eot_id|>"
                prompt += "<|start_header_id|>assistant<|end_header_id|>\n\n"
                return prompt
            else:
                # Default ChatML
                full_prompt = f"<|im_start|>system\n{system_rules}<|im_end|>\n"
                for msg in messages:
                    if msg['role'] != 'system':
                        full_prompt += f"<|im_start|>{msg['role']}\n{msg['content']}<|im_end|>\n"
                return full_prompt + "<|im_start|>assistant\n"

    def _process_actions(self, response: str) -> List[str]:
        """Process actions dari response dengan rate limiting dan loop protection."""
        results = []
        extracted_commands = []

        # 1. Tangkap tag <shell> eksplisit
        shell_tag_pattern = r'<shell>(.*?)(?=</shell>|<file|<shell|$)'
        for match in re.findall(shell_tag_pattern, response, re.DOTALL | re.IGNORECASE):
            cmd = re.sub(r'</shell>', '', match, flags=re.IGNORECASE).strip()
            if cmd and cmd not in extracted_commands:
                extracted_commands.append(cmd)

        # 2. Tangkap blok markdown code (fallback)
        markdown_pattern = r'```(?:shell|bash|sh)\s*\n?(.*?)\n?```'
        for match in re.findall(markdown_pattern, response, re.DOTALL | re.IGNORECASE):
            cmd = match.strip()
            if cmd and cmd not in extracted_commands:
                extracted_commands.append(cmd)

        # Eksekusi perintah shell dengan rate limiting
        for cmd in extracted_commands:
            if len(cmd) < 2:
                continue

            # Rate limiting - tunggu cooldown antar perintah
            now = time.time()
            time_since_last = now - self._last_command_time
            if time_since_last < self._command_cooldown:
                sleep_time = self._command_cooldown - time_since_last
                logger.info(f"Rate limiting: waiting {sleep_time:.2f}s before executing '{cmd}'")
                time.sleep(sleep_time)
            self._last_command_time = time.time()

            # Circuit breaker - stop jika terlalu banyak failure berturut-turut
            if self._consecutive_failures >= self._max_consecutive_failures:
                logger.error(f"Circuit breaker triggered: {self._consecutive_failures} consecutive failures")
                console.print(Panel(f"[bold red]Circuit Breaker: Terlalu banyak kegagalan perintah. Hentikan eksekusi.[/bold red]", border_style="red"))
                results.append(f"Perintah '{cmd}' GAGAL: Circuit breaker aktif - terlalu banyak kegagalan.")
                break

            # Cek perintah interaktif
            if any(cmd.startswith(ic) or ic in cmd for ic in INTERACTIVE_COMMANDS):
                console.print(Panel(f"[bold red]Perintah interaktif '{cmd}' tidak didukung.[/bold red]", border_style="red"))
                results.append(f"Perintah '{cmd}' GAGAL: Perintah interaktif tidak didukung.")
                self._consecutive_failures += 1
                continue

            self.state = AronState.EXECUTING

            # Tentukan apakah auto-confirm layak
            auto_confirm = False
            # Cek apakah perintah dimulai dengan salah satu base command
            for base in AUTO_CONFIRM_BASE:
                if cmd.startswith(base):
                    # Periksa karakter berbahaya
                    if re.search(r'[;&|`$()<>]', cmd):
                        console.print(Panel(f"[bold yellow]Perintah '{cmd}' mengandung karakter berbahaya, konfirmasi manual.[/bold yellow]", border_style="yellow"))
                        auto_confirm = False
                        break
                    else:
                        auto_confirm = True
                        break

            # Untuk perintah cat, cek ukuran file secara lebih cerdas
            if cmd.startswith("cat "):
                # Parse dengan shlex
                try:
                    parts = shlex.split(cmd)
                    # Cari argumen yang bukan opsi
                    file_candidates = [p for p in parts[1:] if not p.startswith('-')]
                    if file_candidates:
                        filepath = file_candidates[-1]
                        # Expand ~ dan relative path
                        filepath = os.path.expanduser(filepath)
                        if not os.path.isabs(filepath):
                            filepath = os.path.join(self.cwd, filepath)
                        if os.path.exists(filepath) and os.path.getsize(filepath) > 50 * 1024:  # 50KB
                            console.print(Panel(f"[bold yellow]File besar (>50KB) akan di-cat. Konfirmasi manual.[/bold yellow]", border_style="yellow"))
                            auto_confirm = False
                except:
                    pass  # Jika parsing gagal, fallback ke aturan biasa

            if auto_confirm:
                # Silent execution untuk auto-confirm commands
                res = self._run_shell(cmd)
                self.state = AronState.VERIFYING
                if res.success:
                    # Reset failure counter on success
                    self._consecutive_failures = 0
                    output = res.output if res.output.strip() else "(tidak ada output)"
                    # Truncation cerdas
                    if len(output) > 2000:
                        output = output[:1000] + "\n... [output dipotong karena terlalu panjang] ...\n" + output[-1000:]
                        console.print("[yellow]⚠ Output sangat panjang, dipotong untuk efisiensi.[/yellow]")
                    results.append(f"Output perintah '{cmd}':\n{output}")
                else:
                    # Graceful error handling - jangan tampilkan panel merah
                    logger.debug(f"Command failed: {res.error}")
                    results.append(f"Perintah '{cmd}' GAGAL: {res.error}")
                    # Tambahkan error ke context agar AI bisa adapt
                    console.print(f"[dim]  (Note: {res.error})[/dim]")
                continue  # Skip confirmation panel untuk auto-confirm
            
            # Non-auto-confirm commands tampilkan panel
            console.print(Panel(f"[bold yellow]{cmd}[/bold yellow]", title="Perintah Sistem (Auto-Detected)", border_style="yellow"))
            try:
                confirm = questionary.confirm("Jalankan perintah di atas? (ESC to cancel)", default=True).ask()
                if confirm is None:  # ESC pressed
                    console.print("[dim]  Command cancelled.[/dim]")
                    continue
            except KeyboardInterrupt:
                console.print("[dim]  Command cancelled.[/dim]")
                continue

            if confirm:
                res = self._run_shell(cmd)
                self.state = AronState.VERIFYING
                if res.success:
                    self._consecutive_failures = 0
                    console.print(f"[bold green]✓ Berhasil[/bold green]")
                    output = res.output if res.output.strip() else "(tidak ada output)"
                    if len(output) > 2000:
                        output = output[:1000] + "\n... [truncated] ...\n" + output[-1000:]
                        console.print("[yellow]⚠ Output sangat panjang, dipotong.[/yellow]")
                    results.append(f"Output perintah '{cmd}':\n{output}")
                else:
                    self._consecutive_failures += 1
                    logger.warning(f"Command failed ({self._consecutive_failures}/{self._max_consecutive_failures}): {res.error}")
                    console.print(f"[bold red]✗ Gagal: {res.error}[/bold red]")
                    results.append(f"Perintah '{cmd}' GAGAL: {res.error}")

        # 3. Tangkap tag <file>
        file_pattern = r'<file\s+path=["\'](.*?)["\']>(.*?)(?=</file>|<file|<shell|$)'
        for path, content_raw in re.findall(file_pattern, response, re.DOTALL | re.IGNORECASE):
            path = path.strip()
            content = re.sub(r'</file>', '', content_raw, flags=re.IGNORECASE).strip()
            if not content:
                continue
            self.state = AronState.EXECUTING
            console.print(Panel(f"[bold blue]Update File:[/bold blue] [cyan]{path}[/cyan]", border_style="blue"))
            if questionary.confirm(f"Tulis perubahan ke {path}?", default=True).ask():
                try:
                    self.patcher.write_full_file(path, content)
                    console.print(f"[bold green]✓ File diperbarui[/bold green]")
                    results.append(f"File {path} diperbarui.")
                except Exception as e:
                    console.print(f"[bold red]✗ Gagal: {e}[/bold red]")
        return results

    def _run_shell(self, cmd: str) -> ExecutionResult:
        # Tangani cd secara khusus
        if cmd.startswith("cd "):
            path = cmd[3:].strip()
            try:
                # Expand user dan relative path
                path = os.path.expanduser(path)
                if not os.path.isabs(path):
                    path = os.path.join(self.cwd, path)
                os.chdir(path)
                self.cwd = os.getcwd()
                return ExecutionResult(True, "", "", 0)
            except Exception as e:
                return ExecutionResult(False, "", str(e), 1)
        else:
            try:
                process = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=self.cwd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return ExecutionResult(
                    process.returncode == 0,
                    process.stdout,
                    process.stderr,
                    process.returncode
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(False, "", "Command timed out", 124)
            except Exception as e:
                return ExecutionResult(False, "", str(e), 1)