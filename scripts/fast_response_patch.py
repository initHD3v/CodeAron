#!/usr/bin/env python3
"""
Quick fix script untuk simplifikasi response Aron.
Patch orchestrator untuk direct response pada command sederhana.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.orchestrator import Orchestrator
import re

# Save original run_cycle
original_run_cycle = Orchestrator.run_cycle

def simplified_run_cycle(self, initial_input: str):
    """
    Simplified run_cycle dengan fast path untuk command sederhana.
    """
    from rich.panel import Panel
    
    self.metrics.start_request()

    # === FAST PATH: Direct responses ===
    
    # 1. Greeting - langsung response
    greetings = ["hai", "halo", "hi", "p", "siapa ini", "pagi", "siang", "sore", "malam"]
    if initial_input.lower().strip() in greetings:
        response = "Halo! Saya Aron. Ada yang bisa saya bantu?"
        self.chat_history.append({"role": "User", "content": initial_input})
        self.chat_history.append({"role": "Aron", "content": response})
        self.console.print(self.ui.render_message("Aron", response))
        return response
    
    # 2. Simple shell commands - langsung execute
    simple_patterns = [r"^ls\s", r"^ls$", r"^pwd$", r"^head\s", r"^tail\s", r"^cat\s", r"^grep\s", r"^which\s", r"^echo\s"]
    is_simple = any(re.match(pattern, initial_input.strip()) for pattern in simple_patterns)
    
    if is_simple:
        result = self._run_shell(initial_input.strip())
        if result.success:
            output = result.output if result.output.strip() else "(no output)"
            if len(output) > 3000:
                output = output[:1500] + "\n... [truncated] ...\n" + output[-1500:]
            self.console.print(Panel(output, title=f"Output: {initial_input.strip()}", border_style="green"))
            self.chat_history.append({"role": "User", "content": initial_input})
            self.chat_history.append({"role": "Aron", "content": f"Executed: {initial_input.strip()}"})
            return output
        else:
            self.console.print(f"[red]Error: {result.error}[/red]")
            return result.error
    
    # === SLOW PATH: Cognitive loop untuk task kompleks ===
    # Fallback ke original implementation untuk task kompleks
    return original_run_cycle(self, initial_input)

# Monkey patch
Orchestrator.run_cycle = simplified_run_cycle

print("✓ Patch applied: Simplified response enabled")
print("  - Greeting: Direct response")
print("  - Simple shell (ls, cat, etc): Direct execution")
print("  - Complex tasks: Full cognitive loop")

# Now run aron
from src.main import app

if __name__ == "__main__":
    app()
