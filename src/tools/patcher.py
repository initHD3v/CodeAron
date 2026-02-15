import os
import difflib
from pathlib import Path
from typing import List, Tuple
from rich.console import Console

console = Console()

class CodePatcher:
    """Mesin utama untuk menulis dan menambal (patching) kode secara cerdas."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)

    def write_full_file(self, relative_path: str, content: str) -> bool:
        """Menulis seluruh isi file. Digunakan untuk file baru."""
        try:
            full_path = self.project_root / relative_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            console.print(f"[bold red]Gagal menulis file {relative_path}:[/bold red] {str(e)}")
            return False

    def patch_file(self, relative_path: str, search_block: str, replace_block: str) -> bool:
        """
        Menambal file dengan mencari blok tertentu dan menggantinya.
        Mirip dengan cara kerja alat 'replace' tetapi di sisi lokal Aron.
        """
        try:
            full_path = self.project_root / relative_path
            if not full_path.exists():
                return False

            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            if search_block in content:
                new_content = content.replace(search_block, replace_block)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                return True
            else:
                # Coba fuzzy matching jika block tidak ketemu persis (misal masalah spasi)
                console.print(f"[yellow]Peringatan: Blok pencarian tidak ditemukan persis di {relative_path}. Mencoba alternatif...[/yellow]")
                return False
        except Exception as e:
            console.print(f"[bold red]Gagal menambal file {relative_path}:[/bold red] {str(e)}")
            return False

    def preview_diff(self, relative_path: str, new_content: str):
        """Menampilkan diff perbandingan sebelum menulis."""
        full_path = self.project_root / relative_path
        if not full_path.exists():
            console.print(f"[green]File Baru: {relative_path}[/green]")
            return

        with open(full_path, "r", encoding="utf-8") as f:
            old_lines = f.readlines()
        
        new_lines = new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines, new_lines, 
            fromfile=f"a/{relative_path}", 
            tofile=f"b/{relative_path}"
        )
        
        for line in diff:
            if line.startswith('+'):
                console.print(f"[green]{line.strip()}[/green]")
            elif line.startswith('-'):
                console.print(f"[red]{line.strip()}[/red]")
            else:
                console.print(f"[dim]{line.strip()}[/dim]")
