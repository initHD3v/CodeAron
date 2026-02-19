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

# System Config
from src.core.config import settings
from src.core.states import AronState, ExecutionResult
from src.llm.inference import InferenceEngine
from src.tools.patcher import CodePatcher
from src.tools.validator import ValidationEngine
from src.memory.vector_store import VectorStore
from src.memory.indexer import ProjectIndexer
from src.llm.hub import ModelHub
from src.ui.renderer import UIRenderer, ARON_THEME

# New Cognitive Modules
from src.core.planner import TaskPlanner
from src.core.router import ToolRouter
from src.core.critic import SelfCritic
from src.core.confidence import ConfidenceEngine
from src.core.metrics import MetricsTracker
from src.core.memory import MemoryManager, ContextCompressor
from src.core.recovery import RecoveryEngine, retry_with_backoff

console = Console(theme=ARON_THEME)
logger = logging.getLogger("Orchestrator")

class Orchestrator:
    def __init__(self):
        self.chat_history: List[Dict[str, str]] = []
        self.process = psutil.Process(os.getpid())
        self.state = AronState.IDLE
        self._last_stats = {"ram": 0.0, "cpu": 0.0}
        self._last_update_time = 0.0
        
        self.inference = InferenceEngine()
        self.patcher = CodePatcher(str(settings.CURRENT_PROJECT_DIR))
        self.validator = ValidationEngine(str(settings.CURRENT_PROJECT_DIR))
        self.ui = UIRenderer()
        
        try:
            self.vector_store = VectorStore()
        except:
            self.vector_store = None
        
        # Initialize Cognitive Engines
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
        now = time.time()
        if now - self._last_update_time > 3.0:
            try:
                mem_info = self.process.memory_info()
                self._last_stats = {
                    "ram": mem_info.rss / (1024 ** 3),
                    "cpu": psutil.cpu_percent() 
                }
                self._last_update_time = now
            except: pass
        return self._last_stats

    def _shutdown(self):
        console.print("\n")
        # Merender summary sebelum semua komponen ditutup
        console.print(self.ui.render_shutdown_summary(self.chat_history))
        
        # Penutupan komponen secara eksplisit untuk menghindari error Qdrant/sys.meta_path
        try:
            if hasattr(self, 'vector_store') and self.vector_store:
                self.vector_store.close()
            if hasattr(self, 'inference') and self.inference:
                self.inference.unload_model()
        except: pass
        
        sys.exit(0)

    def _signal_handler(self, sig, frame):
        # Ctrl+C sekarang memicu shutdown bersih dengan summary
        self._shutdown()

    def interactive_session(self):
        # Auto-indexing if database is empty
        if self.vector_store and self.vector_store.count_points() == 0:
            indexer = ProjectIndexer(str(settings.CURRENT_PROJECT_DIR), self.vector_store)
            indexer.scan_project()

        commands = ["/help", "/clear", "/hub", "/update", "/quit"]
        session = PromptSession(
            completer=WordCompleter(commands, ignore_case=True),
            bottom_toolbar=lambda: HTML(self.ui.render_status_bar(
                self._get_resource_usage()['ram'], self._get_resource_usage()['cpu'], self.state.value
            )),
            style=Style.from_dict({'bottom-toolbar': '#ffffff bg:#1a1a1a'}),
            refresh_interval=2.0
        )
        
        console.clear()
        console.print(self.ui.generate_header(settings.VERSION, os.path.basename(self.inference.model_path)))
        
        while True:
            try:
                user_input = session.prompt(f"╭─❯ ")
                if not user_input.strip(): continue
                if user_input == "/quit": break
                if user_input == "/clear":
                    self.chat_history = []; console.clear()
                    console.print(self.ui.generate_header(settings.VERSION, os.path.basename(self.inference.model_path)))
                    continue
                
                if user_input == "/hub":
                    from src.llm.hub import ModelHub
                    ModelHub().display_hub()
                    continue

                if user_input == "/help":
                    self.ui.render_help()
                    continue

                if user_input == "/update":
                    from src.tools.updater import AronUpdater
                    AronUpdater().run_update()
                    continue
                
                self.run_cycle(user_input)
            except (KeyboardInterrupt, EOFError): break
        self._shutdown()

    def run_cycle(self, initial_input: str):
        self.metrics.start_request()
        self.metrics.log_transition(self.state.value, AronState.ANALYZING.value)
        self.state = AronState.ANALYZING
        
        depth: int = 0
        current_input: str = initial_input
        refinement_count: int = 0
        max_refinement: int = 2 # Prevent infinite loops
        
        while depth < 5:
            try:
                # 1. PLANNING PHASE
                self.metrics.log_transition(self.state.value, AronState.PLANNING.value)
                self.state = AronState.PLANNING
                
                # Context loading via MemoryManager (3-Layer Architecture)
                raw_context = self.memory.get_combined_context(current_input)
                comp_context = self.compressor.compress(raw_context)
                
                # Use TaskPlanner to adjust depth/strategy
                task_plan = self.planner.create_plan(current_input, comp_context)
                
                # 2. ROUTING PHASE
                self.metrics.log_transition(self.state.value, AronState.ROUTING.value)
                self.state = AronState.ROUTING
                routing_info = self.router.route(current_input, comp_context)

                # 3. EXECUTION PHASE
                self.metrics.log_transition(self.state.value, AronState.EXECUTING.value)
                self.state = AronState.EXECUTING
                
                # Apply Model Routing from Router
                selected_model = routing_info.get("selected_model", "default")
                
                prompt = self._build_prompt(current_input, comp_context)
                full_response = ""
                
                old_settings = termios.tcgetattr(sys.stdin)
                try:
                    termios.tcflush(sys.stdin, termios.TCIFLUSH)
                    tty.setcbreak(sys.stdin.fileno())
                    
                    with Live(console=console, refresh_per_second=4) as live:
                        for chunk in self.inference.generate_stream(
                            prompt, temp=0.1, # Forced deterministic
                            stop_sequences=[
                                "<｜User｜>", "<｜Assistant｜>", "User:", "Assistant:", 
                                "\n\n", "[List of commands]", "• /", "\n•"
                            ]
                        ):
                            full_response += chunk
                            live.update(Group(
                                self.ui.render_message("Aron", full_response),
                                self.ui.render_live_status(self._get_resource_usage()['ram'], self._get_resource_usage()['cpu'])
                            ))
                            if select.select([sys.stdin], [], [], 0)[0]:
                                if sys.stdin.read(1) == '\x1b': break
                finally:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

                # 4. ACTION PROCESSING
                action_results = self._process_actions(full_response)
                
                # 5. SELF-CRITIC PHASE
                self.metrics.log_transition(self.state.value, AronState.CRITIQUING.value)
                self.state = AronState.CRITIQUING
                critic_feedback = self.critic.evaluate(current_input, full_response)
                
                if self.critic.needs_refinement(critic_feedback) and refinement_count < max_refinement:
                    self.metrics.log_transition(self.state.value, AronState.REFINING.value)
                    self.state = AronState.REFINING
                    refinement_count += 1
                    current_input = f"[CRITIC FEEDBACK]: {json.dumps(critic_feedback.flaws)}\nPlease correct the above issues."
                    continue

                # 6. VERIFICATION & FINALIZATION
                self.metrics.log_transition(self.state.value, AronState.VERIFYING.value)
                self.state = AronState.VERIFYING
                
                clean_response = re.sub(r'^(Aron|Assistant|User|\[RESPONSE\]):\s*', '', full_response, flags=re.MULTILINE | re.IGNORECASE).strip()
                clean_response = re.sub(r'<｜.*?｜>', '', clean_response)
                
                # Update Memory Systems
                self.memory.add_short_term("User", current_input)
                self.memory.add_short_term("Aron", clean_response)
                
                self.chat_history.append({"role": "User", "content": current_input})
                self.chat_history.append({"role": "Aron", "content": clean_response})
                
                if not action_results:
                    break
                
                current_input = "\n".join(action_results)
                if len(current_input) > 4000:
                    current_input = current_input[:4000] + "\n... (output truncated)"
                
                depth += 1
                console.print(f"\n[dim italic] ● Berpikir... (Putaran {int(depth)}/5)[/dim italic]")

            except Exception as e:
                logger.error(f"Cycle failed: {e}")
                # Fallback via RecoveryEngine
                recovery_res = RecoveryEngine.fallback_result(str(e))
                self.chat_history.append({"role": "Aron", "content": recovery_res['output']})
                
                self.metrics.log_transition(self.state.value, AronState.FAILED.value)
                self.state = AronState.FAILED
                break
        
        # Calculate Confidence & Log Metrics
        # Section 11: Learning Mode (Explain why changes were made)
        learning_mode = getattr(settings, "LEARNING_MODE", False)
        
        confidence_metadata = {
            "confidence": self.confidence_engine.calculate_score(
                critic_severity=critic_feedback.severity_score,
                tool_success=bool(action_results),
                retry_count=refinement_count,
                model_certainty=1.0,
                learning_mode=learning_mode
            ),
            "tools_used": ["shell", "file_patcher"] if action_results else ["none"],
            "iterations": depth + 1,
            "model": "deepseek-coder-local",
            "learning_mode": learning_mode
        }
        
        metrics_log = self.metrics.end_request({
            "intent": initial_input[:50],
            "model_used": os.path.basename(self.inference.model_path) if hasattr(self.inference, 'model_path') else "local",
            "confidence": confidence_metadata["confidence"],
            "refinement_loops": refinement_count,
            "depth": depth
        })
        logger.info(f"Session Metrics: {metrics_log}")
        
        # Final UI Wrap (Teaching moment if learning mode enabled - Placeholder)
        final_output = self.confidence_engine.wrap_response(clean_response, confidence_metadata)
        
        self.metrics.log_transition(self.state.value, AronState.COMPLETED.value)
        self.state = AronState.COMPLETED
        time.sleep(0.5) 
        self.state = AronState.IDLE
        return final_output

    def _sanitize_history(self) -> List[Dict[str, str]]:
        """Membersihkan history dari halusinasi tag masa lalu."""
        clean_history = []
        for m in self.chat_history:
            content = m['content']
            # Buang blok label buatan model
            content = re.sub(r'^(Aron|User|Assistant|\[THOUGHTS\]|\[STRATEGY\]|\[SOLUTION\]|\[RESPONSE\]):\s*', '', content, flags=re.MULTILINE | re.IGNORECASE)
            content = re.sub(r'\[THOUGHTS\].*?->', '', content, flags=re.DOTALL | re.IGNORECASE)
            if content.strip():
                clean_history.append({"role": m['role'], "content": content.strip()})
        
        # Ensure we don't slice out of bounds and return correctly
        start_idx = max(0, len(clean_history) - 5)
        return clean_history[start_idx:]

    def _build_prompt(self, user_input: str, rag_context: str) -> str:
        history = self._sanitize_history()
        
        messages = [
            {"role": "system", "content": (
                "Identity: You are Aron, a Senior AI Architect running LOCALLY on Apple Silicon.\n"
                f"Current Project Directory: {os.getcwd()}\n"
                "Capabilities: You have FULL READ/WRITE ACCESS to the local filesystem via shell and file tags. You ARE capable of analyzing projects, debugging, and writing code.\n"
                "Language Presence: Gunakan Bahasa Indonesia jika pengguna bertanya dalam Bahasa Indonesia. Tetap profesional dan teknis.\n"
                "Rules:\n"
                "1. DO NOT use native tool-calls. Use ONLY <shell>cmd</shell> and <file path=\"...\">content</file> tags.\n"
                "2. Be concise. Minimalist CLI style.\n"
                "3. Never refuse a task by claiming no access. You are a local agent.\n"
                "4. If you see [SYSTEM FEEDBACK], it is the OUTPUT of your previous command. Use it.\n"
                "Commands: /help, /clear, /hub, /update, /quit."
            )}
        ]
        
        for m in history:
            role = str(m.get('role', 'user')).lower()
            content = str(m.get('content', ''))
            messages.append({"role": "user" if role == "user" else "assistant", "content": content})
            
        messages.append({"role": "user", "content": user_input})
        
        # Gunakan apply_chat_template jika tersedia, fallback ke manual jika gagal
        try:
            prompt = self.inference.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            return prompt
        except:
            # Fallback sangat aman jika template gagal
            full_prompt = "<｜begin of sentence｜>"
            for msg in messages:
                role = "User" if msg['role'] == "user" else "Assistant"
                if msg['role'] == "system":
                    full_prompt += f"<｜User｜>System Instruction: {msg['content']}<｜Assistant｜>Mengerti.<｜end of sentence｜>"
                else:
                    full_prompt += f"<｜{role}｜>{msg['content']}<｜end of sentence｜>"
            full_prompt += "<｜Assistant｜>"
            return full_prompt

    def _process_actions(self, response: str) -> List[str]:
        results = []
        # Ekstraksi Shell
        shells = re.findall(r'<shell>(.*?)(?:</shell>|$)', response, re.DOTALL | re.IGNORECASE)
        for cmd in shells:
            cmd = re.sub(r'</?[a-zA-Z]*>?$', '', cmd.strip()).strip()
            if not cmd or len(cmd) < 2: continue
            
            self.state = AronState.EXECUTING
            if questionary.confirm(f"Jalankan perintah: {cmd}?", default=True).ask():
                res = self._run_shell(cmd)
                self.state = AronState.VALIDATING
                if res.success:
                    console.print(f"[bold green]✓ Success[/bold green]")
                    results.append(f"[SYSTEM FEEDBACK]: [COMMAND OUTPUT]:\n{res.output}")
                else:
                    console.print(f"[bold red]✗ Failed: {res.error}[/bold red]")
                    results.append(f"[SYSTEM FEEDBACK]: [COMMAND ERROR]:\n{res.error if res.error else res.output}")

        # Ekstraksi File
        files = re.findall(r'<file\s+path=[\'"](.*?)[\'"]>(.*?)(?:</file>|$)', response, re.DOTALL | re.IGNORECASE)
        for path, content in files:
            path = path.strip()
            content = re.sub(r'</?[a-zA-Z]*>?$', '', content.strip()).strip()
            if not content: continue
            
            self.state = AronState.EXECUTING
            if questionary.confirm(f"Tulis ke file: {path}?", default=True).ask():
                self._patch_file(path, content)
                results.append(f"[SYSTEM FEEDBACK]: [FILE NOTIFICATION]: File {path} has been updated.")
        
        return results

    def _run_shell(self, cmd: str) -> ExecutionResult:
        try:
            # Tambahkan timeout 30 detik agar tidak hang pada direktori besar
            process = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return ExecutionResult(process.returncode == 0, process.stdout, process.stderr, process.returncode)
        except subprocess.TimeoutExpired:
            return ExecutionResult(False, "", "Command timed out after 30 seconds.", 124)
        except Exception as e: 
            return ExecutionResult(False, "", str(e), 1)

    def _patch_file(self, path: str, content: str):
        try:
            self.patcher.write_full_file(path, content)
            console.print(f"[bold green]✓ File updated[/bold green]")
        except Exception as e: console.print(f"[bold red]✗ Patch error: {e}[/bold red]")
