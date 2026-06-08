from __future__ import annotations

import shutil

from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from habits import __version__


def _terminal_width(console: Console) -> int:
    detected = shutil.get_terminal_size(fallback=(console.size.width, 24)).columns
    return max(24, min(console.size.width, detected))


def _append_centered(lines: Text, value: str, content_width: int, style: str = "") -> None:
    for index, line in enumerate(value.splitlines()):
        if index:
            lines.append("\n")
        lines.append(line.center(content_width), style=style)


def show_welcome(console: Console, *, user_name: str, active_count: int, left_margin: int = 0) -> None:
    width = _terminal_width(console)
    available_width = max(24, width - left_margin)
    banner_width = max(24, (available_width * 2) // 3)
    content_width = max(12, banner_width - 4)
    lines = Text()

    _append_centered(lines, f"Habits  v{__version__}", content_width, "bold cyan")
    lines.append("\n")
    _append_centered(lines, "Rastreador de hábitos", content_width, "bold")
    lines.append("\n")
    _append_centered(lines, f"{user_name} · {active_count} hábitos ativos", content_width, "green")

    panel = Panel(lines, border_style="cyan", padding=(0, 1), width=banner_width)
    if left_margin:
        console.print(Padding(panel, (0, 0, 0, left_margin)))
    else:
        console.print(panel)
