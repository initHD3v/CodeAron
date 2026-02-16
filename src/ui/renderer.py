import re
from rich.theme import Theme
from rich.style import Style
from rich.panel import Panel
from rich.text import Text
from rich.console import Group
from rich.table import Table
from rich.markdown import Markdown

# Definisi Tema Profesional CodeAron
ARON_THEME = Theme({
    "aron.primary": "bold cyan",
    "aron.secondary": "dim white",
    "aron.user": "bold green",
    "aron.system": "italic dim yellow",
    "aron.error": "bold red",
    "aron.header": "white on blue",
    "aron.footer": "black on white",
    "aron.border": "dim cyan",
    "markdown.code": "bold cyan",
    "markdown.code_block": "white on #1e1e1e"
})

class UIRenderer:
    @staticmethod
    def generate_header(version: str, model_name: str):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left")
        grid.add_column(justify="right")
        grid.add_row(
            Text(f" 🤖 CodeAron v{version}", style="aron.primary"),
            Text(f"Model: {model_name} ", style="aron.secondary")
        )
        return Panel(grid, style="aron.border", padding=0)

    @staticmethod
    def render_message(role: str, content: str):
        color = "aron.user" if role.lower() == "user" else "aron.primary"
        prefix = " ● Kamu" if role.lower() == "user" else " ● Aron"
        
        if role.lower() == "user":
            renderable = Text(content, style="white")
        else:
            clean_content = re.sub(r'</file>', '', content, flags=re.IGNORECASE)
            clean_content = re.sub(
                r'<file\s+path=[\'"](.*?)[\'"]>', 
                r'\n---\n> 📄 **FILE:** `\1` \n', 
                clean_content, 
                flags=re.IGNORECASE
            )
            renderable = Markdown(clean_content, code_theme="monokai")
        
        message_group = Group(
            Text(f"{prefix}\n", style=color),
            renderable
        )
        
        return Panel(
            message_group,
            border_style="aron.border" if role.lower() != "user" else "green",
            padding=(1, 2),
            expand=True
        )

    @staticmethod
    def render_status_bar(ram: float, cpu: float, status: str = "Idle"):
        # Format untuk prompt_toolkit (Bottom Toolbar)
        ram_color = "#00ff00" if ram < 8 else "#ffff00" if ram < 16 else "#ff0000"
        cpu_color = "#00ff00" if cpu < 50 else "#ff0000"
        return (
            f" <b>STATUS:</b> {status} | "
            f"<b>RAM:</b> <style fg='{ram_color}'>{ram:.1f}GB</style> | "
            f"<b>CPU:</b> <style fg='{cpu_color}'>{cpu:.0f}%</style> "
        )

    @staticmethod
    def render_live_status(ram: float, cpu: float):
        # Format untuk Rich (saat streaming respons)
        ram_color = "green" if ram < 8 else "yellow" if ram < 16 else "red"
        cpu_color = "green" if cpu < 50 else "red"
        return f"\n [dim]RAM: [{ram_color}]{ram:.1f}GB[/{ram_color}] | CPU: [{cpu_color}]{cpu:.0f}%[/{cpu_color}][/dim]"
