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


def _ask_panel_choice(
    console: Console,
    choices: list[str],
    default: str,
    *,
    allow_commands: bool = False,
    transient: bool = False,
) -> str:
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

        if value in choices:
            sys.stdout.write("\033[2A\r\033[J" if transient else "\033[1B\r")
            sys.stdout.flush()
            return value
        if allow_commands and any(character.isalpha() for character in value):
            sys.stdout.write("\033[2A\r\033[J" if transient else "\033[1B\r")
            sys.stdout.flush()
            return value
        if transient:
            sys.stdout.write("\033[2A\r\033[J")
        else:
            sys.stdout.write("\033[1B\r")
            lines_to_clear = 4 if warning else 3
            sys.stdout.write(f"\033[{lines_to_clear}A\033[J")
        sys.stdout.flush()
        warning = "Escolha inválida."


def _ask_boxed_text(console: Console, label: str, *, default: str = "", transient: bool = False) -> str:
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
    if transient:
        sys.stdout.write("\033[2A\r\033[J")
    else:
        sys.stdout.write("\033[1B\r")
    sys.stdout.flush()
    return value or default


def _confirm_pt(console: Console, message: str, *, default: bool = False) -> bool:
    default_text = "S" if default else "N"
    while True:
        raw_value = _ask_boxed_text(console, f"{message} [S/N]", default=default_text, transient=True).strip()
        value = raw_value.lower()
        if value in {"s", "sim"}:
            console.print(" " * LEFT_MARGIN + "[green]Confirmação: S[/green]")
            return True
        if value in {"n", "nao", "não"}:
            console.print(" " * LEFT_MARGIN + "[yellow]Confirmação: N[/yellow]")
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
    raw_number = _ask_boxed_text(console, "Número do hábito, ou Enter para voltar", transient=True).strip()
    if not raw_number:
        return None
    if not raw_number.isdigit():
        console.print("[red]Número inválido.[/red]")
        _pause(console)
        return None
    habit_number = int(raw_number)
    if not 1 <= habit_number <= len(habits):
        console.print("[red]Hábito não encontrado.[/red]")
        _pause(console)
        return None
    habit = habits[habit_number - 1]
    habit_id = int(habit["id"])
    console.print(" " * LEFT_MARGIN + f'[green]Hábito selecionado: {habit_number}. {habit["name"]}[/green]')
    return habit_id


def _select_habit_from_matches(console: Console, matches: list[dict]) -> int | None:
    if not matches:
        console.print("[yellow]Nenhum hábito encontrado com esse nome.[/yellow]")
        return None
    if len(matches) == 1:
        return int(matches[0]["id"])
    console.print("[yellow]Encontrei mais de um hábito. Escolha qual usar:[/yellow]")
    for index, habit in enumerate(matches, start=1):
        console.print(f'{index}. {habit["icon"]} {habit["name"]}')
    raw_number = _ask_boxed_text(console, "Número do hábito, ou Enter para cancelar", transient=True).strip()
    if not raw_number:
        return None
    if not raw_number.isdigit():
        console.print("[red]Número inválido.[/red]")
        _pause(console)
        return None
    habit_number = int(raw_number)
    if not 1 <= habit_number <= len(matches):
        console.print("[red]Número fora da lista encontrada.[/red]")
        _pause(console)
        return None
    habit = matches[habit_number - 1]
    habit_id = int(habit["id"])
    console.print(" " * LEFT_MARGIN + f'[green]Hábito selecionado: {habit_number}. {habit["name"]}[/green]')
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
    choice = _ask_panel_choice(console, ["1", "2", "3"], "1", transient=True)
    frequency = {"1": "daily", "2": "weekdays", "3": "weekly"}[choice]
    console.print(" " * LEFT_MARGIN + f"[green]Frequência: {frequency_label(frequency)}[/green]")
    return frequency


def _ask_weekly_target(console: Console) -> int:
    while True:
        value = _ask_boxed_text(console, "Quantas vezes por semana? 1-7", default="3", transient=True)
        if value.isdigit() and 1 <= int(value) <= 7:
            target = int(value)
            console.print(" " * LEFT_MARGIN + f"[green]Meta semanal: {target}[/green]")
            return target
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


def register_flow(console: Console, conn: sqlite3.Connection, habit_id: int | None = None) -> bool:
    habit_id = habit_id or _select_habit(console, conn)
    if habit_id is None:
        return False
    if models.entry_exists(conn, habit_id) and not _confirm_pt(console, "Este hábito já foi registrado hoje. Atualizar?", default=False):
        return True
    duration = Prompt.ask("Duração opcional (90, 90min, 1h, 1h30)", default="")
    note = Prompt.ask("Nota opcional", default="")
    try:
        entry = models.register_entry(conn, habit_id, duration_minutes=duration, note=note)
    except ValueError as exc:
        console.print(f"[red]Duração inválida. Use formatos como 90, 90min, 1h ou 1h30.[/red]")
        return True
    console.print(f'[green]Registro salvo para {entry["date"]}.[/green]')
    return True


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


def delete_habit_flow(console: Console, conn: sqlite3.Connection) -> None:
    habit_id = _select_habit(console, conn, active=None)
    if habit_id is None:
        return
    habit = models.get_habit(conn, habit_id)
    console.print()
    console.print("[red]Atenção: apagar é definitivo e remove todo o histórico deste hábito.[/red]")
    console.print(f'Hábito selecionado: {habit["icon"]} {habit["name"]}')
    typed_name = _ask_boxed_text(console, "Digite o nome exato para confirmar", transient=True)
    if typed_name != habit["name"]:
        console.print("[yellow]Nome diferente. Exclusão cancelada.[/yellow]")
        return
    console.print(" " * LEFT_MARGIN + f"[green]Nome confirmado: {typed_name}[/green]")
    if not _confirm_pt(console, "Apagar definitivamente?", default=False):
        console.print("[yellow]Exclusão cancelada.[/yellow]")
        return
    models.delete_habit(conn, habit_id)
    console.print("[green]Hábito apagado definitivamente.[/green]")


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
            actions.append(("delete", "Apagar hábito"))
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
        elif action == "delete":
            _render_screen(console, conn, "Apagar hábito")
            delete_habit_flow(console, conn)
            _pause(console)
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
        console.print()
        panels.print_paths(console)
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
            "2. Guia de comandos",
            "3. Configurações",
            "4. Sair",
        ],
    )
    choice = _ask_panel_choice(console, ["1", "2", "3", "4"], "1")
    if choice == "1":
        _render_screen(console, conn, "Criar hábito")
        create_habit_flow(console, conn)
        _pause(console)
    elif choice == "2":
        _render_screen(console, conn, "Guia de comandos")
        panels.print_guide(console)
        _pause(console)
    elif choice == "3":
        config_flow(console, conn)
    else:
        _clear_terminal(console, scrollback=True)
        return False
    return True


def _run_inline_command(console: Console, conn: sqlite3.Connection, raw_command: str) -> bool:
    parts = raw_command.strip().split()
    if not parts:
        return False
    if parts[0].lower() == "habits":
        parts = parts[1:]
    if not parts:
        return False

    command = parts[0].lower()
    query = " ".join(parts[1:]).strip()
    if command in {"check", "registrar"}:
        _render_screen(console, conn, "Registrar hábito")
        habit_id = select_habit_by_query(console, conn, query, active=True) if query else None
        if register_flow(console, conn, habit_id):
            _pause(console)
        return True
    if command in {"hoje", "today"}:
        _render_screen(console, conn, "Menu do dia")
        panels.print_today(console, conn)
        _pause(console)
        return True
    if command in {"streak", "sequencia", "sequência"}:
        _render_screen(console, conn, "Sequências")
        panels.print_streaks(console, conn)
        _pause(console)
        return True
    if command in {"historico", "histórico", "history"}:
        _render_screen(console, conn, "Histórico")
        habit_id = select_habit_by_query(console, conn, query, active=None) if query else None
        history_flow(console, conn, habit_id, interactive=not bool(habit_id))
        _pause(console)
        return True
    if command in {"db", "banco"}:
        _render_screen(console, conn, "Banco de dados")
        panels.print_db(console, conn)
        _pause(console)
        return True
    if command in {"help", "ajuda", "guia", "comandos"}:
        _render_screen(console, conn, "Guia de comandos")
        panels.print_guide(console)
        _pause(console)
        return True
    if command in {"paths", "caminhos"}:
        _render_screen(console, conn, "Caminhos")
        panels.print_paths(console)
        _pause(console)
        return True

    _render_screen(console, conn, "Comando inválido")
    _empty_state(console, f"Não reconheci o comando: {raw_command}")
    _pause(console)
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
                    ("register", "Registrar hábito"),
                    ("today", "Menu do dia"),
                    ("streaks", "Sequências"),
                ]
            )
        actions.append(("manage", "Gerenciar hábitos"))
        actions.extend(
            [
                ("guide", "Guia de comandos"),
                ("config", "Configurações"),
                ("exit", "Sair"),
            ]
        )
        choices = [str(index) for index in range(1, len(actions) + 1)]
        default_choice = choices[-1]

        _render_screen(console, conn, "Menu principal")
        _print_options_panel(console, [f"{index}. {label}" for index, (_, label) in enumerate(actions, start=1)])
        choice = _ask_panel_choice(console, choices, default_choice, allow_commands=True)
        if choice not in choices:
            _run_inline_command(console, conn, choice)
            continue
        action = actions[int(choice) - 1][0]
        if action == "today":
            _render_screen(console, conn, "Menu do dia")
            panels.print_today(console, conn)
            _pause(console)
        elif action == "register":
            _render_screen(console, conn, "Registrar hábito")
            if register_flow(console, conn):
                _pause(console)
        elif action == "manage":
            manage_flow(console, conn)
        elif action == "streaks":
            _render_screen(console, conn, "Sequências")
            panels.print_streaks(console, conn)
            _pause(console)
        elif action == "guide":
            _render_screen(console, conn, "Guia de comandos")
            panels.print_guide(console)
            _pause(console)
        elif action == "config":
            config_flow(console, conn)
        else:
            _clear_terminal(console, scrollback=True)
            return
