from __future__ import annotations

import sqlite3

from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt

from habits import models
from habits.config import load_config, reset_config, save_config
from habits.palette import PALETTE
from habits.ui import panels
from habits.ui.welcome import show_welcome


def _select_habit(console: Console, conn: sqlite3.Connection) -> int | None:
    habits = models.list_habits(conn, active=True)
    if not habits:
        console.print("[yellow]Nenhum hábito ativo ainda.[/yellow]")
        return None
    panels.print_habits(console, conn, active=True)
    habit_id = IntPrompt.ask("ID do hábito")
    if not any(habit["id"] == habit_id for habit in habits):
        console.print("[red]Hábito não encontrado.[/red]")
        return None
    return habit_id


def create_habit_flow(console: Console, conn: sqlite3.Connection) -> None:
    name = Prompt.ask("Nome do hábito").strip()
    icon = Prompt.ask("Ícone", default="⭐")
    console.print("Cores: " + ", ".join(PALETTE))
    color = Prompt.ask("Cor", default="azul")
    frequency = Prompt.ask(
        "Frequência",
        choices=["daily", "weekdays", "weekly", "diario", "dias_uteis", "x_por_semana"],
        default="daily",
    )
    target = 1
    if models.normalize_frequency(frequency) == "weekly":
        target = IntPrompt.ask("Quantas vezes por semana?", default=3)
    goal_text = Prompt.ask("Meta diária em minutos (opcional)", default="")
    goal = int(goal_text) if goal_text.strip().isdigit() else None
    habit = models.create_habit(
        conn,
        name,
        icon=icon,
        color=color,
        frequency_type=frequency,
        frequency_target=target,
        daily_goal_minutes=goal,
    )
    console.print(f'[green]Hábito criado:[/green] {habit["icon"]} {habit["name"]}')


def register_flow(console: Console, conn: sqlite3.Connection) -> None:
    habit_id = _select_habit(console, conn)
    if habit_id is None:
        return
    if models.entry_exists(conn, habit_id) and not Confirm.ask("Este hábito já foi registrado hoje. Atualizar?", default=False):
        return
    duration = Prompt.ask("Duração opcional (90, 90min, 1h, 1h30)", default="")
    note = Prompt.ask("Nota opcional", default="")
    try:
        entry = models.register_entry(conn, habit_id, duration_minutes=duration, note=note)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        return
    console.print(f'[green]Registro salvo para {entry["date"]}.[/green]')


def manage_flow(console: Console, conn: sqlite3.Connection) -> None:
    while True:
        console.print("\n[bold]Gerenciar hábitos[/bold]")
        console.print("1. Criar hábito")
        console.print("2. Listar ativos")
        console.print("3. Arquivar hábito")
        console.print("4. Listar arquivados")
        console.print("5. Voltar")
        choice = Prompt.ask("Escolha", choices=["1", "2", "3", "4", "5"], default="5")
        if choice == "1":
            create_habit_flow(console, conn)
        elif choice == "2":
            panels.print_habits(console, conn, active=True)
        elif choice == "3":
            habit_id = _select_habit(console, conn)
            if habit_id is not None and Confirm.ask("Arquivar este hábito?", default=False):
                models.archive_habit(conn, habit_id)
                console.print("[green]Hábito arquivado.[/green]")
        elif choice == "4":
            panels.print_habits(console, conn, active=False)
        else:
            return


def config_flow(console: Console) -> None:
    config = load_config()
    while True:
        console.print("\n[bold]Configurações[/bold]")
        console.print(f'1. Nome: {config["user_name"]}')
        console.print(f'2. Saudação: {"ligada" if config["show_greeting"] else "desligada"}')
        console.print(f'3. Cor padrão: {config["default_color"]}')
        console.print("4. Resetar configuração")
        console.print("5. Voltar")
        choice = Prompt.ask("Escolha", choices=["1", "2", "3", "4", "5"], default="5")
        if choice == "1":
            config["user_name"] = Prompt.ask("Novo nome", default=config["user_name"])
            save_config(config)
        elif choice == "2":
            config["show_greeting"] = not config["show_greeting"]
            save_config(config)
        elif choice == "3":
            console.print("Cores: " + ", ".join(PALETTE))
            config["default_color"] = Prompt.ask("Cor", default=config["default_color"])
            save_config(config)
        elif choice == "4":
            if Confirm.ask("Resetar configuração?", default=False):
                config = reset_config()
        else:
            return


def show_menu(console: Console, conn: sqlite3.Connection) -> None:
    config = load_config()
    show_welcome(
        console,
        user_name=config["user_name"],
        active_count=len(models.list_habits(conn, active=True)),
        greeting=config["show_greeting"],
    )
    while True:
        console.print("\n[bold]Menu principal[/bold]")
        console.print("1. Resumo do dia")
        console.print("2. Registrar hábito")
        console.print("3. Gerenciar hábitos")
        console.print("4. Sequências")
        console.print("5. Banco de dados")
        console.print("6. Configurações")
        console.print("7. Caminhos")
        console.print("8. Sair")
        choice = Prompt.ask("Escolha", choices=[str(i) for i in range(1, 9)], default="8")
        if choice == "1":
            panels.print_today(console, conn)
        elif choice == "2":
            register_flow(console, conn)
        elif choice == "3":
            manage_flow(console, conn)
        elif choice == "4":
            panels.print_streaks(console, conn)
        elif choice == "5":
            panels.print_db(console, conn)
        elif choice == "6":
            config_flow(console)
        elif choice == "7":
            panels.print_paths(console)
        else:
            return
