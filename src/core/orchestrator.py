from typing import Optional, Dict, Any
from .states import AronState
from .config import settings
from src.llm.inference import InferenceEngine
from src.tools.git_guard import GitGuard
from src.tools.flutter_bridge import FlutterBridge
from rich.console import Console
from rich.panel import Panel

console = Console()

class Orchestrator:
    def __init__(self):
        self.current_state: AronState = AronState.IDLE
        self.context: Dict[str, Any] = {}
        self.retry_count: int = 0
        self.max_retries: int = settings.MAX_RETRIES if hasattr(settings, "MAX_RETRIES") else 3
        
        # Tools initialization
        self.inference = InferenceEngine()
        self.git = GitGuard(str(settings.BASE_DIR))
        self.bridge = FlutterBridge()

    def transition_to(self, new_state: AronState):
        """Mengelola transisi antar state dengan logging visual."""
        icon = "🚀" if new_state == AronState.PLANNING else "🔧" if new_state == AronState.CODING else "✅"
        console.log(f"[bold blue]State Transition:[/bold blue] {self.current_state.value} {icon} [bold cyan]{new_state.value}[/bold cyan]")
        self.current_state = new_state

    def run_step(self, user_input: str):
        """Alur logika utama transaksional."""
        try:
            # 1. INITIALIZING & PLANNING
            self.transition_to(AronState.INITIALIZING)
            self.git.create_checkpoint()
            
            self.transition_to(AronState.PLANNING)
            console.print(Panel(f"[italic]{user_input}[/italic]", title="User Request", border_style="green"))
            
            # 2. CODING (Simulasi untuk saat ini)
            self.transition_to(AronState.CODING)
            # Di sini nantinya LLM akan men-generate kode
            
            # 3. VALIDATING
            self.transition_to(AronState.VALIDATING)
            success = self.bridge.run_analyze()
            
            if success:
                self.transition_to(AronState.COMMITTING)
                self.git.commit_changes(f"Aron: {user_input}")
                console.print("\n[bold green]✨ Pekerjaan selesai dengan sempurna![/bold green]")
            else:
                self._handle_failure()

            self.transition_to(AronState.IDLE)
            
        except Exception as e:
            console.log(f"[bold red]Error Fatal:[/bold red] {str(e)}")
            self.git.rollback()
            self.transition_to(AronState.ERROR)

    def _handle_failure(self):
        """Menangani kegagalan validasi dengan retry atau rollback."""
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            console.print(f"[bold yellow]⚠️ Validasi gagal. Mencoba memperbaiki (Attempt {self.retry_count}/{self.max_retries})...[/bold yellow]")
            self.transition_to(AronState.HEALING)
            # Logika healing akan memanggil LLM kembali dengan pesan error
        else:
            console.print("[bold red]❌ Gagal setelah percobaan maksimal. Melakukan Rollback.[/bold red]")
            self.git.rollback()
            self.transition_to(AronState.IDLE)
