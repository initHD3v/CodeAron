import typer
import questionary
from src.core.orchestrator import Orchestrator
from src.core.config import settings
from src.llm.hub import ModelHub
from src.ui.renderer import ARON_THEME
from rich.console import Console
from rich.panel import Panel

from src.tools.updater import AronUpdater

app = typer.Typer(name=settings.APP_NAME)
console = Console(theme=ARON_THEME)
hub = ModelHub()
updater = AronUpdater()
orchestrator = None

def display_banner():
    banner = (
        "[bold cyan]    ██████╗ ██████╗ ██████╗ ███████╗ █████╗ ██████╗  ██████╗ ███╗   ██╗[/bold cyan]\n"
        "[bold cyan]    ██╔═══╝ ██║  ██║██║  ██║██╔════╝██╔══██╗██╔══██╗██╔═══██╗████╗  ██║[/bold cyan]\n"
        "[bold cyan]    ██║     ██║  ██║██║  ██║█████╗  ███████║██████╔╝██║   ██║██╔██╗ ██║[/bold cyan]\n"
        "[bold cyan]    ██║     ██║  ██║██║  ██║██╔══╝  ██╔══██║██╔══██╗██║   ██║██║╚██╗██║[/bold cyan]\n"
        "[bold cyan]    ╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║██║  ██║╚██████╔╝██║ ╚████║[/bold cyan]\n"
        "[dim]     ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝[/dim]"
    )
    console.print(banner)
    console.print(f" [bold white]CodeAron v{settings.VERSION}[/bold white] | [italic dim white]Apple Silicon Optimized[/italic dim white]")
    
    if updater.check_for_updates():
        console.print(f" [bold yellow]✨ Versi baru tersedia! Ketik [bold white]/update[/bold white] untuk memperbarui.[/bold yellow]")
def get_orchestrator():
    global orchestrator
    if orchestrator is None:
        try:
            orchestrator = Orchestrator()
        except Exception as e:
            console.print(f"[bold red]Gagal inisialisasi:[/bold red] {e}")
            raise typer.Exit(code=1)
    return orchestrator

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        display_banner()
        try:
            with console.status("[bold cyan]Memulai mesin AI Aron...[/bold cyan]\n[dim](Download model semantik mungkin terjadi saat pertama kali jalan)[/dim]"):
                orc = get_orchestrator()
            orc.interactive_session()
        except Exception as e:
            console.print(f"[bold red]Critical Error:[/bold red] {e}")

@app.command()
def chat(prompt: str = typer.Argument(..., help="Perintah untuk Aron")):
    """Mulai percakapan dengan CodeAron"""
    orc = get_orchestrator()
    orc.run_cycle(prompt)

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
