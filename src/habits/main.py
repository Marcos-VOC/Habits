from __future__ import annotations

import sys

from rich.console import Console

from . import __version__
from .db import connect, init_db
from .models import list_habits
from .ui import menu, panels


ALIASES = {
    "check": "check",
    "registrar": "check",
    "hoje": "today",
    "today": "today",
    "streak": "streak",
    "sequencia": "streak",
    "sequência": "streak",
    "db": "db",
    "banco": "db",
    "help": "help",
    "ajuda": "help",
    "--help": "help",
    "-h": "help",
    "paths": "paths",
    "caminhos": "paths",
    "version": "version",
    "--version": "version",
}


HELP = f"""
Habits v{__version__}

Comandos rápidos:
  habits                    menu interativo completo
  habits check|registrar    marcar hábitos de hoje
  habits hoje|today         resumo rápido do dia
  habits streak|sequencia   ver sequências atuais
  habits db|banco           visualizar tabelas do banco
  habits paths|caminhos     mostrar caminhos do app
  habits help|ajuda         este guia
"""


def resolve_command(argv: list[str]) -> str | None:
    if not argv:
        return None
    return ALIASES.get(argv[0].lower(), "help")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    console = Console()
    command = resolve_command(args)

    with connect() as conn:
        init_db(conn)
        if command is None:
            menu.show_menu(console, conn)
        elif command == "check":
            menu.register_flow(console, conn)
        elif command == "today":
            panels.print_today(console, conn)
        elif command == "streak":
            panels.print_streaks(console, conn)
        elif command == "db":
            panels.print_db(console, conn)
        elif command == "paths":
            panels.print_paths(console)
        elif command == "version":
            console.print(f"Habits v{__version__}")
        else:
            console.print(HELP)
            if list_habits(conn, active=True):
                console.print("Dica: use [bold]habits hoje[/bold] para ver o resumo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
