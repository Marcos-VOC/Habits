from __future__ import annotations

import sqlite3
import sys

from rich.console import Console
from rich.prompt import Prompt

from habits import models
from habits.config import load_config, reset_config, save_config
from habits.palette import PALETTE, normalize_color
from habits.ui import panels
from habits.ui.labels import frequency_label
from habits.ui.welcome import show_welcome


LEFT_MARGIN = 2
ICON_SUGGESTIONS = ["⭐", "📘", "🏋️", "🧘", "💧", "🏃", "🧠", "🎯", "🎸", "🌱"]


def _clear_terminal(console: Console, *, scrollback: bool = False) -> None:
    if console.is_terminal:
        prefix = "\033[3J" if scrollback else ""
        sys.stdout.write(prefix + "\033[H\033[2J")
        sys.stdout.flush()
        return
    console.clear()


def _render_screen(console: Console, conn: sqlite3.Connection, title: str | None = None) -> None:
    config = load_config()
    _clear_terminal(console)
    show_welcome(
        console,
        user_name=config["user_name"],
        active_count=len(models.list_habits(conn, active=True)),
        left_margin=LEFT_MARGIN,
    )
    if title:
        console.print()
        console.print(" " * LEFT_MARGIN + f"[bold]{title}[/bold]")


def _menu_panel_width(console: Console) -> int:
    available_width = max(28, console.size.width - LEFT_MARGIN)
    return min(available_width, max(28, (available_width * 2) // 3))


def _print_options_panel(console: Console, options: list[str]) -> None:
    prefix = " " * LEFT_MARGIN
    console.print("\n".join(prefix + option for option in options))


def _ask_panel_choice(console: Console, choices: list[str], default: str) -> str:
    warning: str | None = None
    while True:
        width = _menu_panel_width(console)
        inner_width = max(12, width - 4)
        label = f"Escolha [{'/'.join(choices)}]  ({default}): "
        if len(label) > inner_width:
            label = "Escolha: "

        top = "╭" + "─" * (width - 2) + "╮"
        middle = "│ " + label + " " * max(0, inner_width - len(label)) + " │"
        bottom = "╰" + "─" * (width - 2) + "╯"
        prefix = " " * LEFT_MARGIN

        if warning:
            console.print(prefix + f"[red]{warning}[/red]")
        console.print(prefix + top, style="cyan")
        console.print(prefix + middle, style="cyan")
        console.print(prefix + bottom, style="cyan")
        sys.stdout.write(f"\033[2A\r\033[{LEFT_MARGIN + len('│ ' + label) + 1}C")
        sys.stdout.flush()
        value = input().strip() or default
        sys.stdout.write("\033[1B\r")
        sys.stdout.flush()

        if value in choices:
            return value
        lines_to_clear = 4 if warning else 3
        sys.stdout.write(f"\033[{lines_to_clear}A\033[J")
        sys.stdout.flush()
        warning = "Escolha inválida."


def _ask_boxed_text(console: Console, label: str, *, default: str = "") -> str:
    width = _menu_panel_width(console)
    inner_width = max(12, width - 4)
    suffix = f" ({default}): " if default else ": "
    prompt = label + suffix
    if len(prompt) > inner_width:
        prompt = label[: max(1, inner_width - len(suffix))] + suffix

    top = "╭" + "─" * (width - 2) + "╮"
    middle = "│ " + prompt + " " * max(0, inner_width - len(prompt)) + " │"
    bottom = "╰" + "─" * (width - 2) + "╯"
    prefix = " " * LEFT_MARGIN

    console.print(prefix + top, style="cyan")
    console.print(prefix + middle, style="cyan")
    console.print(prefix + bottom, style="cyan")
    sys.stdout.write(f"\033[2A\r\033[{LEFT_MARGIN + len('│ ' + prompt) + 1}C")
    sys.stdout.flush()
    value = input().strip()
    sys.stdout.write("\033[1B\r")
    sys.stdout.flush()
    return value or default


def _confirm_pt(console: Console, message: str, *, default: bool = False) -> bool:
    default_text = "S" if default else "N"
    while True:
        value = _ask_boxed_text(console, f"{message} [S/N]", default=default_text).strip().lower()
        if value in {"s", "sim"}:
            return True
        if value in {"n", "nao", "não"}:
            return False
        console.print(" " * LEFT_MARGIN + "[red]Responda com S ou N.[/red]")


def _pause(console: Console, message: str = "Pressione Enter para voltar") -> None:
    width = _menu_panel_width(console)
    inner_width = max(12, width - 4)
    label = message + " "
    if len(label) > inner_width:
        label = "Enter para voltar "
    top = "╭" + "─" * (width - 2) + "╮"
    middle = "│ " + label + " " * max(0, inner_width - len(label)) + " │"
    bottom = "╰" + "─" * (width - 2) + "╯"
    prefix = " " * LEFT_MARGIN

    console.print()
    console.print(prefix + top, style="cyan")
    console.print(prefix + middle, style="cyan")
    console.print(prefix + bottom, style="cyan")
    sys.stdout.write(f"\033[2A\r\033[{LEFT_MARGIN + len('│ ' + label) + 1}C")
    sys.stdout.flush()
    input()
    sys.stdout.write("\033[1B\r")
    sys.stdout.flush()


def _empty_state(console: Console, message: str) -> None:
    console.print(" " * LEFT_MARGIN + f"[yellow]{message}[/yellow]")


def _select_habit(console: Console, conn: sqlite3.Connection, *, active: bool | None = True) -> int | None:
    habits = models.list_habits(conn, active=active)
    if not habits:
        _empty_state(console, "Nenhum hábito encontrado.")
        return None
    panels.print_habits(console, conn, active=active)
    raw_id = Prompt.ask("ID do hábito, ou Enter para voltar", default="").strip()
    if not raw_id:
        return None
    if not raw_id.isdigit():
        console.print("[red]ID inválido.[/red]")
        _pause(console)
        return None
    habit_id = int(raw_id)
    if not any(habit["id"] == habit_id for habit in habits):
        console.print("[red]Hábito não encontrado.[/red]")
        _pause(console)
        return None
    return habit_id


def _select_habit_from_matches(console: Console, matches: list[dict]) -> int | None:
    if not matches:
        console.print("[yellow]Nenhum hábito encontrado com esse nome.[/yellow]")
        return None
    if len(matches) == 1:
        return int(matches[0]["id"])
    console.print("[yellow]Encontrei mais de um hábito. Escolha qual usar:[/yellow]")
    for habit in matches:
        console.print(f'{habit["id"]}. {habit["icon"]} {habit["name"]}')
    raw_id = Prompt.ask("ID do hábito, ou Enter para cancelar", default="").strip()
    if not raw_id:
        return None
    if not raw_id.isdigit():
        console.print("[red]ID inválido.[/red]")
        _pause(console)
        return None
    habit_id = int(raw_id)
    if not any(habit["id"] == habit_id for habit in matches):
        console.print("[red]ID fora da lista encontrada.[/red]")
        _pause(console)
        return None
    return habit_id


def select_habit_by_query(
    console: Console,
    conn: sqlite3.Connection,
    query: str,
    *,
    active: bool | None = True,
) -> int | None:
    return _select_habit_from_matches(console, models.find_habits(conn, query, active=active))


def _ask_required_text(console: Console, label: str, *, cancel_text: str = "n") -> str | None:
    while True:
        value = Prompt.ask(label).strip()
        if value:
            return value
        console.print(f"[red]{label} não pode ficar vazio.[/red]")
        retry = Prompt.ask("Pressione Enter para tentar novamente ou N para cancelar", default="")
        if retry.strip().lower() == cancel_text:
            return None


def _ask_optional_minutes(console: Console, label: str) -> int | None:
    while True:
        value = Prompt.ask(label, default="").strip()
        if not value:
            return None
        if value.isdigit():
            return int(value)
        console.print("[red]Informe um número inteiro de minutos ou deixe vazio.[/red]")


def _ask_frequency(console: Console) -> str:
    _print_options_panel(
        console,
        [
            "1. Todos os dias (1 registro por dia)",
            "2. Segunda a sexta",
            "3. X vezes por semana",
        ],
    )
    choice = _ask_panel_choice(console, ["1", "2", "3"], "1")
    return {"1": "daily", "2": "weekdays", "3": "weekly"}[choice]


def _ask_weekly_target(console: Console) -> int:
    while True:
        value = _ask_boxed_text(console, "Quantas vezes por semana? 1-7", default="3")
        if value.isdigit() and 1 <= int(value) <= 7:
            return int(value)
        console.print(" " * LEFT_MARGIN + "[red]A meta semanal deve ficar entre 1 e 7.[/red]")


def _ask_icon(console: Console) -> str:
    console.print("Sugestões de ícones: " + "  ".join(ICON_SUGGESTIONS))
    console.print("[dim]Você pode digitar qualquer emoji ou caractere curto que seu terminal suporte.[/dim]")
    return Prompt.ask("Ícone", default="⭐").strip() or "⭐"


def create_habit_flow(console: Console, conn: sqlite3.Connection) -> None:
    name = _ask_required_text(console, "Nome do hábito")
    if name is None:
        console.print("[yellow]Criação cancelada.[/yellow]")
        return
    icon = _ask_icon(console)
    console.print("Cores: " + ", ".join(PALETTE))
    color = Prompt.ask("Cor", default="azul")
    frequency = _ask_frequency(console)
    target = 1
    if frequency == "weekly":
        target = _ask_weekly_target(console)
    goal = _ask_optional_minutes(console, "Meta diária em minutos (opcional)")
    color = normalize_color(color)
    console.print()
    console.print("Confirme os dados do hábito:")
    console.print(f"Nome: {name}")
    console.print(f"Ícone: {icon}")
    console.print(f"Cor: {color}")
    console.print(f"Frequência: {frequency_label(frequency)}")
    if frequency == "weekly":
        console.print(f"Meta semanal: {target}")
    console.print(f"Meta diária: {goal if goal is not None else 'sem meta'}")
    if not _confirm_pt(console, "Criar hábito com esses dados?", default=True):
        console.print("[yellow]Criação cancelada.[/yellow]")
        return
    try:
        habit = models.create_habit(
            conn,
            name,
            icon=icon,
            color=color,
            frequency_type=frequency,
            frequency_target=target,
            daily_goal_minutes=goal,
        )
    except ValueError:
        console.print("[red]Não foi possível criar o hábito. Confira os dados informados.[/red]")
        return
    console.print(f'[green]Hábito criado:[/green] {habit["icon"]} {habit["name"]}')


def register_flow(console: Console, conn: sqlite3.Connection, habit_id: int | None = None) -> None:
    habit_id = habit_id or _select_habit(console, conn)
    if habit_id is None:
        return
    if models.entry_exists(conn, habit_id) and not _confirm_pt(console, "Este hábito já foi registrado hoje. Atualizar?", default=False):
        return
    duration = Prompt.ask("Duração opcional (90, 90min, 1h, 1h30)", default="")
    note = Prompt.ask("Nota opcional", default="")
    try:
        entry = models.register_entry(conn, habit_id, duration_minutes=duration, note=note)
    except ValueError as exc:
        console.print(f"[red]Duração inválida. Use formatos como 90, 90min, 1h ou 1h30.[/red]")
        return
    console.print(f'[green]Registro salvo para {entry["date"]}.[/green]')


def history_flow(
    console: Console,
    conn: sqlite3.Connection,
    habit_id: int | None = None,
    *,
    interactive: bool = False,
) -> None:
    if interactive:
        while True:
            habit_id = _select_habit(console, conn, active=None)
            if habit_id is None:
                return
            habit = models.get_habit(conn, habit_id)
            _render_screen(console, conn, f'Histórico - {habit["icon"]} {habit["name"]}')
            panels.print_habit_history(console, conn, habit_id)
            _pause(console)
            _render_screen(console, conn, "Histórico")

    habit_id = habit_id or _select_habit(console, conn, active=None)
    if habit_id is None:
        return
    panels.print_habit_history(console, conn, habit_id)


def manage_flow(console: Console, conn: sqlite3.Connection) -> None:
    while True:
        active_habits = models.list_habits(conn, active=True)
        archived_habits = models.list_habits(conn, active=False)
        all_habits = models.list_habits(conn, active=None)
        actions = [("create", "Criar hábito")]
        if active_habits:
            actions.extend(
                [
                    ("list_active", "Listar ativos"),
                    ("archive", "Arquivar hábito"),
                ]
            )
        if archived_habits:
            actions.extend(
                [
                    ("list_archived", "Listar arquivados"),
                    ("unarchive", "Desarquivar hábito"),
                ]
            )
        if all_habits:
            actions.append(("history", "Histórico por hábito"))
        actions.append(("back", "Voltar"))
        choices = [str(index) for index in range(1, len(actions) + 1)]
        default_choice = choices[-1]

        _render_screen(console, conn, "Gerenciar hábitos")
        _print_options_panel(console, [f"{index}. {label}" for index, (_, label) in enumerate(actions, start=1)])
        choice = _ask_panel_choice(console, choices, default_choice)
        action = actions[int(choice) - 1][0]
        if action == "create":
            _render_screen(console, conn, "Criar hábito")
            create_habit_flow(console, conn)
            _pause(console)
        elif action == "list_active":
            _render_screen(console, conn, "Hábitos ativos")
            panels.print_habits(console, conn, active=True)
            _pause(console)
        elif action == "archive":
            _render_screen(console, conn, "Arquivar hábito")
            habit_id = _select_habit(console, conn)
            if habit_id is None:
                continue
            if _confirm_pt(console, "Arquivar este hábito?", default=False):
                models.archive_habit(conn, habit_id)
                console.print("[green]Hábito arquivado.[/green]")
            _pause(console)
        elif action == "list_archived":
            _render_screen(console, conn, "Hábitos arquivados")
            panels.print_habits(console, conn, active=False)
            _pause(console)
        elif action == "unarchive":
            _render_screen(console, conn, "Desarquivar hábito")
            habit_id = _select_habit(console, conn, active=False)
            if habit_id is None:
                continue
            if _confirm_pt(console, "Desarquivar este hábito?", default=True):
                models.unarchive_habit(conn, habit_id)
                console.print("[green]Hábito desarquivado.[/green]")
            _pause(console)
        elif action == "history":
            _render_screen(console, conn, "Histórico por hábito")
            history_flow(console, conn, interactive=True)
        else:
            return


def config_flow(console: Console, conn: sqlite3.Connection) -> None:
    config = load_config()
    while True:
        _render_screen(console, conn, "Configurações")
        _print_options_panel(
            console,
            [
                f'1. Nome: {config["user_name"]}',
                f'2. Cor padrão: {config["default_color"]}',
                "3. Resetar configuração",
                "4. Voltar",
            ],
        )
        choice = _ask_panel_choice(console, ["1", "2", "3", "4"], "4")
        if choice == "1":
            config["user_name"] = Prompt.ask("Novo nome", default=config["user_name"])
            save_config(config)
        elif choice == "2":
            console.print("Cores: " + ", ".join(PALETTE))
            config["default_color"] = Prompt.ask("Cor", default=config["default_color"])
            save_config(config)
        elif choice == "3":
            if _confirm_pt(console, "Resetar configuração?", default=False):
                config = reset_config()
        else:
            return


def empty_database_menu(console: Console, conn: sqlite3.Connection) -> bool:
    _render_screen(console, conn, "Primeiros passos")
    _empty_state(console, "Nenhum hábito criado ainda. Crie seu primeiro hábito para liberar as telas do dia a dia.")
    _print_options_panel(
        console,
        [
            "1. Criar hábito",
            "2. Banco de dados",
            "3. Guia de comandos",
            "4. Caminhos",
            "5. Configurações",
            "6. Sair",
        ],
    )
    choice = _ask_panel_choice(console, ["1", "2", "3", "4", "5", "6"], "1")
    if choice == "1":
        _render_screen(console, conn, "Criar hábito")
        create_habit_flow(console, conn)
        _pause(console)
    elif choice == "2":
        _render_screen(console, conn, "Banco de dados")
        panels.print_db(console, conn)
        _pause(console)
    elif choice == "3":
        _render_screen(console, conn, "Guia de comandos")
        panels.print_guide(console)
        _pause(console)
    elif choice == "4":
        _render_screen(console, conn, "Caminhos")
        panels.print_paths(console)
        _pause(console)
    elif choice == "5":
        config_flow(console, conn)
    else:
        _clear_terminal(console, scrollback=True)
        return False
    return True


def show_menu(console: Console, conn: sqlite3.Connection) -> None:
    _clear_terminal(console, scrollback=True)
    while True:
        all_habits = models.list_habits(conn, active=None)
        active_habits = models.list_habits(conn, active=True)
        if not all_habits:
            if not empty_database_menu(console, conn):
                return
            continue

        actions = []
        if active_habits:
            actions.extend(
                [
                    ("today", "Resumo do dia"),
                    ("register", "Registrar hábito"),
                    ("streaks", "Sequências"),
                ]
            )
        actions.append(("manage", "Gerenciar hábitos"))
        actions.append(("db", "Banco de dados"))
        if all_habits:
            actions.append(("history", "Histórico"))
        actions.extend(
            [
                ("guide", "Guia de comandos"),
                ("config", "Configurações"),
                ("paths", "Caminhos"),
                ("exit", "Sair"),
            ]
        )
        choices = [str(index) for index in range(1, len(actions) + 1)]
        default_choice = choices[-1]

        _render_screen(console, conn, "Menu principal")
        _print_options_panel(console, [f"{index}. {label}" for index, (_, label) in enumerate(actions, start=1)])
        choice = _ask_panel_choice(console, choices, default_choice)
        action = actions[int(choice) - 1][0]
        if action == "today":
            _render_screen(console, conn, "Resumo do dia")
            panels.print_today(console, conn)
            _pause(console)
        elif action == "register":
            _render_screen(console, conn, "Registrar hábito")
            register_flow(console, conn)
            _pause(console)
        elif action == "manage":
            manage_flow(console, conn)
        elif action == "streaks":
            _render_screen(console, conn, "Sequências")
            panels.print_streaks(console, conn)
            _pause(console)
        elif action == "db":
            _render_screen(console, conn, "Banco de dados")
            panels.print_db(console, conn)
            _pause(console)
        elif action == "history":
            _render_screen(console, conn, "Histórico")
            history_flow(console, conn, interactive=True)
        elif action == "guide":
            _render_screen(console, conn, "Guia de comandos")
            panels.print_guide(console)
            _pause(console)
        elif action == "config":
            config_flow(console, conn)
        elif action == "paths":
            _render_screen(console, conn, "Caminhos")
            panels.print_paths(console)
            _pause(console)
        else:
            _clear_terminal(console, scrollback=True)
            return
