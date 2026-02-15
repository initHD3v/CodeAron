import os
from pathlib import Path
from src.memory.models import CodeSymbol, save_symbol, init_db
from rich.console import Console

console = Console()

class ProjectIndexer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        init_db()

    def scan_project(self):
        """Memindai seluruh file .dart di proyek Flutter."""
        console.print(f"Memindai proyek di: [bold cyan]{self.project_path}[/bold cyan]")
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(".dart"):
                    file_path = os.path.join(root, file)
                    self._index_file(file_path)

    def _index_file(self, file_path: str):
        """Menganalisis file Dart dan mengekstrak simbol (Stub untuk Fase 3)."""
        # Di sini nantinya kita akan menggunakan Tree-sitter untuk parsing yang akurat
        # Untuk saat ini, kita buat placeholder indexing sederhana
        rel_path = os.path.relpath(file_path, self.project_path)
        console.log(f"Mengindeks [dim]{rel_path}[/dim]")
        
        # Contoh simbol placeholder
        # symbol = CodeSymbol(name="Example", type="Class", file_path=rel_path, ...)
        # save_symbol(symbol)
