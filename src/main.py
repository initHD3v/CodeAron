import typer
import questionary
from src.core.orchestrator import Orchestrator
from src.core.config import settings
from src.llm.hub import ModelHub
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(name=settings.APP_NAME)
console = Console()
orchestrator = Orchestrator()
hub = ModelHub()

def display_banner():
    banner = """
    ██████╗ ██████╗ ██████╗ ███████╗ █████╗ ██████╗  ██████╗ ███╗   ██╗
   ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔═══██╗████╗  ██║
   ██║     ██║   ██║██║  ██║█████╗  ███████║██████╔╝██║   ██║██╔██╗ ██║
   ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██║██╔══██╗██║   ██║██║╚██╗██║
   ╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║██║  ██║╚██████╔╝██║ ╚████║
    ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
    """
    console.print(Panel(banner, subtitle=f"v{settings.VERSION} - Local Flutter AI Assistant", border_style="cyan"))

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        display_banner()
        choice = questionary.select(
            "Apa yang ingin Anda lakukan hari ini?",
            choices=[
                "💬 Chat dengan Aron",
                "⚙️ Kelola Model (Hub)",
                "ℹ️ Info Versi",
                "🚪 Keluar"
            ]
        ).ask()
        
        if choice == "💬 Chat dengan Aron":
            prompt = questionary.text("Masukkan perintah Anda:").ask()
            if prompt: chat(prompt)
        elif choice == "⚙️ Kelola Model (Hub)":
            hub_list()
        elif choice == "ℹ️ Info Versi":
            version()

@app.command()
def chat(prompt: str = typer.Argument(..., help="Perintah untuk Aron")):

    """Mulai percakapan dengan CodeAron"""
    console.print(f"[bold cyan]CodeAron v{settings.VERSION}[/bold cyan] siap membantu.\n")
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
