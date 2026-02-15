import typer
import questionary
from src.core.orchestrator import Orchestrator
from src.core.config import settings
from src.llm.hub import ModelHub
from rich.console import Console
from rich.panel import Panel

from src.tools.updater import AronUpdater

app = typer.Typer(name=settings.APP_NAME)
console = Console()
orchestrator = Orchestrator()
hub = ModelHub()
updater = AronUpdater()

def display_banner():
    banner = """
    [bold cyan]██████╗  ██████╗ ██████╗ ███████╗ █████╗ ██████╗  ██████╗ ███╗   ██╗[/bold cyan]
    [bold cyan]██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔═══██╗████╗  ██║[/bold cyan]
    [bold cyan]██║     ██║   ██║██║  ██║█████╗  ███████║██████╔╝██║   ██║██╔██╗ ██║[/bold cyan]
    [bold cyan]██║     ██║   ██║██║  ██║██╔══╝  ██╔══██║██╔══██╗██║   ██║██║╚██╗██║[/bold cyan]
    [bold cyan]╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║██║  ██║╚██████╔╝██║ ╚████║[/bold cyan]
    [bold cyan] ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝[/bold cyan]
    """
    console.print(banner)
    console.print(f"  [bold white]v{settings.VERSION}[/bold white] [dim]|[/dim] [italic cyan]Cerdas, Tangguh, dan Lokal — Your Flutter AI Assistant[/italic cyan]")
    
    # Cek Update
    if updater.check_for_updates():
        console.print(f"  [bold yellow]✨ Versi baru tersedia! Ketik [bold white]/update[/bold white] untuk memperbarui.[/bold yellow]")
    else:
        console.print(f"  [dim]Ketik [bold white]/model[/bold white] untuk kelola AI [dim]|[/dim] [bold white]/quit[/bold white] untuk keluar[/dim]\n")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    display_banner()
    if ctx.invoked_subcommand is None:
        orchestrator.interactive_session()

@app.command()
def chat(prompt: str = typer.Argument(..., help="Perintah untuk Aron")):
    """Mulai percakapan dengan CodeAron"""
    orchestrator.run_step(prompt)

@app.command()
def hub_list():
    """Tampilkan daftar model di Aron Hub"""
    hub.display_hub()

@app.command()
def version():
    """Tampilkan versi CodeAron"""
    console.print(f"{settings.APP_NAME} [bold green]v{settings.VERSION}[/bold green]")

if __name__ == "__main__":
    app()
