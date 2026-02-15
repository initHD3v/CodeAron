from typing import Optional, Dict, Any
from .states import AronState
from rich.console import Console

console = Console()

class Orchestrator:
    def __init__(self):
        self.current_state: AronState = AronState.IDLE
        self.context: Dict[str, Any] = {}
        self.retry_count: int = 0
        self.max_retries: int = 3

    def transition_to(self, new_state: AronState):
        """Mengelola transisi antar state dengan logging."""
        console.log(f"[bold blue]State Transition:[/bold blue] {self.current_state.value} -> {new_state.value}")
        self.current_state = new_state

    def run_step(self, user_input: str):
        """Alur logika utama berdasarkan state saat ini."""
        try:
            if self.current_state == AronState.IDLE:
                self._handle_idle(user_input)
            elif self.current_state == AronState.PLANNING:
                self._handle_planning()
            # State lainnya akan diimplementasikan bertahap
        except Exception as e:
            console.log(f"[bold red]Error in {self.current_state.value}:[/bold red] {str(e)}")
            self.transition_to(AronState.ERROR)

    def _handle_idle(self, user_input: str):
        console.print(f"[bold green]Aron menerima perintah:[/bold green] {user_input}")
        self.context["user_prompt"] = user_input
        self.transition_to(AronState.PLANNING)

    def _handle_planning(self):
        console.print("Aron sedang merancang langkah-langkah...")
        # Integrasi LLM akan masuk di sini pada Fase 2
        self.transition_to(AronState.IDLE)
