import typer
from src.core.orchestrator import Orchestrator
from src.core.config import settings
from rich.console import Console

app = typer.Typer(name=settings.APP_NAME)
console = Console()
orchestrator = Orchestrator()

@app.command()
def chat(prompt: str = typer.Argument(..., help="Perintah untuk Aron")):
    """Mulai percakapan dengan CodeAron"""
    console.print(f"[bold cyan]CodeAron v{settings.VERSION}[/bold cyan] siap membantu.\n")
    orchestrator.run_step(prompt)

@app.command()
def version():
    """Tampilkan versi CodeAron"""
    console.print(f"{settings.APP_NAME} [bold green]v{settings.VERSION}[/bold green]")

if __name__ == "__main__":
    app()
