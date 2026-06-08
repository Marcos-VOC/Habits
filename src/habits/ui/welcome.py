from __future__ import annotations

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from habits import __version__
from habits.paths import db_path


ASCII = r"""
██╗  ██╗ █████╗ ██████╗ ██╗████████╗███████╗
██║  ██║██╔══██╗██╔══██╗██║╚══██╔══╝██╔════╝
███████║███████║██████╔╝██║   ██║   ███████╗
██╔══██║██╔══██║██╔══██╗██║   ██║   ╚════██║
██║  ██║██║  ██║██████╔╝██║   ██║   ███████║
╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝   ╚═╝   ╚══════╝
"""


def show_welcome(console: Console, *, user_name: str, active_count: int, greeting: bool = True) -> None:
    lines = Text()
    lines.append(ASCII.strip("\n"), style="bold cyan")
    lines.append(f"\n\nRastreador de hábitos  v{__version__}", style="bold")
    lines.append(f"\nBanco: {db_path()}", style="dim")
    if greeting:
        lines.append(f"\nOlá, {user_name}! {active_count} hábitos ativos.", style="green")
    panel = Panel(Align.center(lines), border_style="cyan", padding=(1, 2))
    console.print(panel)
