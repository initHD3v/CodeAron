import subprocess
from rich.console import Console

console = Console()

class FlutterBridge:
    @staticmethod
    def run_analyze() -> bool:
        """Menjalankan 'dart analyze' dan mengembalikan True jika sukses (hijau)."""
        console.log("Menjalankan [bold cyan]dart analyze[/bold cyan]...")
        try:
            result = subprocess.run(
                ["dart", "analyze"], 
                capture_output=True, 
                text=True
            )
            if result.returncode == 0:
                console.print("[bold green]Validasi Sukses: Kode bersih.[/bold green]")
                return True
            else:
                console.print("[bold red]Validasi Gagal:[/bold red] Ditemukan masalah pada kode.")
                return False
        except FileNotFoundError:
            console.print("[bold red]Error:[/bold red] Dart SDK tidak ditemukan di PATH.")
            return False

    @staticmethod
    def run_format(file_path: str):
        """Merapikan kode menggunakan 'dart format'."""
        subprocess.run(["dart", "format", file_path], capture_output=True)
