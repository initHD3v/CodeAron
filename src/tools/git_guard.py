import git
from pathlib import Path
from rich.console import Console

console = Console()

class GitGuard:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        try:
            self.repo = git.Repo(repo_path)
        except git.InvalidGitRepositoryError:
            console.print("[bold red]Peringatan:[/bold red] Folder ini bukan repositori Git.")
            self.repo = None

    def create_checkpoint(self, branch_name: str = "aron-working-branch"):
        """Membuat branch baru atau stash untuk mengamankan pekerjaan saat ini."""
        if not self.repo: return
        
        current = self.repo.active_branch
        console.log(f"Membuat checkpoint pada branch: [bold cyan]{branch_name}[/bold cyan]")
        
        # Skenario sederhana: buat branch baru dari HEAD saat ini
        new_branch = self.repo.create_head(branch_name)
        new_branch.checkout()

    def rollback(self):
        """Mengembalikan kondisi ke state aman terakhir."""
        if not self.repo: return
        console.print("[bold orange]Melakukan Rollback otomatis...[/bold orange]")
        self.repo.git.reset('--hard', 'HEAD')

    def commit_changes(self, message: str):
        """Commit perubahan jika validasi sukses."""
        if not self.repo: return
        self.repo.git.add(A=True)
        self.repo.index.commit(message)
        console.log(f"Perubahan berhasil disimpan: [dim]{message}[/dim]")
