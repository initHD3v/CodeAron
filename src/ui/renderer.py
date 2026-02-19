import re
from rich.theme import Theme
from rich.style import Style
from rich.panel import Panel
from rich.text import Text
from rich.console import Group, Console
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

console = Console(theme=ARON_THEME)

class UIRenderer:
    def __init__(self):
        self.console = console

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
        if role.lower() == "user":
            return Group(
                Text(f"\n❯ {content}", style="aron.user"),
            )
        else:
            # 0. Buat salinan konten untuk dibersihkan
            clean_content = content
            
            # Buang token DeepSeek yang mungkin bocor secara agresif
            tokens_to_strip = [
                "<｜User｜>", "<｜Assistant｜>", "<｜end of sentence｜>", "<｜begin of sentence｜>",
                "<｜tool▁call▁begin｜>", "<｜tool▁call▁end｜>", "<｜tool▁sep｜>", "function"
            ]
            for token in tokens_to_strip:
                clean_content = clean_content.replace(token, "")
            
            # Gunakan regex untuk menyaring sisa-sisa tag internal
            clean_content = re.sub(r'<｜.*?｜>', '', clean_content)
            clean_content = re.sub(r'</?file.*?>?', '', clean_content, flags=re.IGNORECASE)
            
            # 2. Ubah <shell> menjadi blok kode agar terlihat di Markdown
            clean_content = re.sub(r'<shell>(.*?)(?:</shell>|$)', r'\n```bash\n\1\n```\n', clean_content, flags=re.DOTALL | re.IGNORECASE)
            
            # Membersihkan sisa-sisa tag penutup
            clean_content = re.sub(r'</?shell>?', '', clean_content, flags=re.IGNORECASE)
            
            if not clean_content.strip():
                # Status berpikir yang sangat minimalis
                return Group(
                    Text("\n ● Berpikir...", style="dim italic"),
                    Text("") 
                )
            
            return Group(
                Markdown(clean_content, code_theme="monokai"),
                Text("") 
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
        # Gunakan Text object agar lebih aman dari MarkupError
        ram_color = "green" if ram < 8 else "yellow" if ram < 16 else "red"
        cpu_color = "green" if cpu < 50 else "red"
        
        status_text = Text()
        status_text.append("\n RAM: ", style="dim")
        status_text.append(f"{ram:.1f}GB", style=ram_color)
        status_text.append(" | ", style="dim")
        status_text.append("CPU: ", style="dim")
        status_text.append(f"{cpu:.0f}%", style=cpu_color)
        status_text.append(" ", style="dim")
        status_text.append("(ESC to stop)", style="dim italic")
        
        return status_text

    @staticmethod
    def render_shutdown_summary(history: list):
        """Merender rangkuman sesi yang cantik saat shutdown."""
        console = Console(theme=ARON_THEME)
        
        # Analisis ringkas dari history
        user_msgs = [m['content'] for m in history if m['role'] == 'User']
        ai_msgs = [m['content'] for m in history if m['role'] == 'Aron']
        
        # Ekstraksi file yang dimodifikasi (estimasi dari history)
        files_modified = set()
        for msg in ai_msgs:
            matches = re.findall(r'<file\s+path=[\'"](.*?)[\'"]>', msg, re.IGNORECASE)
            files_modified.update(matches)

        summary_table = Table(box=None, padding=(0, 1))
        summary_table.add_column("Statistik Sesi", style="aron.primary")
        summary_table.add_column("Nilai", style="white")
        
        summary_table.add_row("Total Percakapan", str(len(user_msgs)))
        summary_table.add_row("File Dimodifikasi", str(len(files_modified)))
        
        if files_modified:
            sorted_files = list(sorted(files_modified))
            limit = 5 if len(sorted_files) > 5 else len(sorted_files)
            file_list = "\n".join([f"  • [dim]{sorted_files[i]}[/dim]" for i in range(limit)])
            if len(sorted_files) > 5: file_list += f"\n  • [dim]...dan {len(sorted_files)-5} lainnya[/dim]"
            summary_table.add_row("Daftar File", file_list)

        panel_content = Group(
            Text("\n✨ Sesi Selesai\n", style="bold cyan", justify="center"),
            summary_table,
            Text("\nKerja bagus hari ini! Sampai ketemu lagi.", style="italic dim white", justify="center"),
            Text("")
        )
        return Panel(panel_content, border_style="aron.border", expand=False)

    @staticmethod
    def render_help():
        table = Table(title="Aron Commands", box=None)
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="white")
        table.add_row("/help", "Tampilkan bantuan ini")
        table.add_row("/clear", "Bersihkan layar dan history chat")
        table.add_row("/hub", "Kelola model AI (Download/List)")
        table.add_row("/update", "Periksa dan instal pembaruan CodeAron")
        table.add_row("/quit", "Keluar dari sesi")
        console.print(Panel(table, title="[bold yellow]Bantuan Perintah[/bold yellow]", border_style="yellow"))
