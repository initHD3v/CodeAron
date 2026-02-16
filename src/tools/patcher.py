import os
import difflib
import logging
from pathlib import Path
from rich.console import Console

console = Console()
logger = logging.getLogger("Patcher")

class CodePatcher:
    """Mesin utama untuk menulis dan menambal kode secara cerdas."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()

    def _safe_path(self, relative_path: str) -> Path:
        """Validasi path untuk mencegah directory traversal."""
        full_path = (self.project_root / relative_path).resolve()
        if not str(full_path).startswith(str(self.project_root)):
            raise ValueError(f"Unauthorized path access: {relative_path}")
        return full_path

    def write_full_file(self, relative_path: str, content: str) -> bool:
        """Menulis seluruh isi file."""
        try:
            full_path = self._safe_path(relative_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"File written: {relative_path}")
            return True
        except Exception as e:
            console.print(f"[bold red]Error writing file {relative_path}:[/bold red] {e}")
            logger.error(f"Write error: {e}")
            return False

    def patch_file(self, relative_path: str, search_block: str, replace_block: str) -> bool:
        """Menambal file dengan mencari blok tertentu dan menggantinya."""
        try:
            full_path = self._safe_path(relative_path)
            if not full_path.exists():
                return False

            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            if search_block in content:
                new_content = content.replace(search_block, replace_block)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                return True
            
            logger.warning(f"Patch block not found in {relative_path}")
            return False
        except Exception as e:
            logger.error(f"Patch error in {relative_path}: {e}")
            return False

    def preview_diff(self, relative_path: str, new_content: str):
        """Menampilkan diff perbandingan sebelum menulis."""
        try:
            full_path = self._safe_path(relative_path)
            if not full_path.exists():
                console.print(f"[green]New File: {relative_path}[/green]")
                return

            with open(full_path, "r", encoding="utf-8") as f:
                old_lines = f.readlines()
            
            new_lines = new_content.splitlines(keepends=True)
            diff = difflib.unified_diff(old_lines, new_lines, fromfile=f"a/{relative_path}", tofile=f"b/{relative_path}")
            
            for line in diff:
                if line.startswith('+'): console.print(f"[green]{line.strip()}[/green]")
                elif line.startswith('-'): console.print(f"[red]{line.strip()}[/red]")
                else: console.print(f"[dim]{line.strip()}[/dim]")
        except Exception as e:
            logger.error(f"Diff error: {e}")
