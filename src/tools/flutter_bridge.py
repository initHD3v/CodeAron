import subprocess
from rich.console import Console

console = Console()

class FlutterBridge:
    @staticmethod
    def run_analyze() -> bool:
        """Menjalankan 'dart analyze' secara silent."""
        try:
            result = subprocess.run(
                ["dart", "analyze"], 
                capture_output=True, 
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    @staticmethod
    def run_format(file_path: str):
        """Merapikan kode menggunakan 'dart format'."""
        subprocess.run(["dart", "format", file_path], capture_output=True)
