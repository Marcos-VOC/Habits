from __future__ import annotations

import sqlite3
from pathlib import Path

from rich.console import Console
from rich.table import Table

from habits import models
from habits.paths import config_path, db_path
from habits.stats import current_streak, streaks_for_habits


def print_today(console: Console, conn: sqlite3.Connection) -> None:
    table = Table(title="Resumo do dia")
    table.add_column("ID", justify="right")
    table.add_column("Hábito")
    table.add_column("Status")
    table.add_column("Duração")
    table.add_column("Nota")
    for item in models.today_summary(conn):
        status = "[green]feito[/green]" if item["done_today"] else "[yellow]pendente[/yellow]"
        duration = str(item["duration_minutes"] or "")
        table.add_row(str(item["id"]), f'{item["icon"]} {item["name"]}', status, duration, item["note"] or "")
    console.print(table)


def print_streaks(console: Console, conn: sqlite3.Connection) -> None:
    table = Table(title="Sequências atuais")
    table.add_column("ID", justify="right")
    table.add_column("Hábito")
    table.add_column("Frequência")
    table.add_column("Sequência", justify="right")
    for item in streaks_for_habits(conn):
        table.add_row(str(item["id"]), f'{item["icon"]} {item["name"]}', item["frequency_type"], str(item["streak"]))
    console.print(table)


def print_habits(console: Console, conn: sqlite3.Connection, *, active: bool | None = True) -> None:
    table = Table(title="Hábitos")
    table.add_column("ID", justify="right")
    table.add_column("Hábito")
    table.add_column("Cor")
    table.add_column("Frequência")
    table.add_column("Meta")
    table.add_column("Sequência", justify="right")
    for habit in models.list_habits(conn, active=active):
        table.add_row(
            str(habit["id"]),
            f'{habit["icon"]} {habit["name"]}',
            habit["color"],
            habit["frequency_type"],
            str(habit["frequency_target"]),
            str(current_streak(conn, habit["id"])),
        )
    console.print(table)


def print_db(console: Console, conn: sqlite3.Connection) -> None:
    for table_name in ("habits", "entries"):
        rows = conn.execute(f"SELECT * FROM {table_name} ORDER BY id").fetchall()
        table = Table(title=table_name)
        columns = [row["name"] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()]
        for column in columns:
            table.add_column(column)
        for row in rows:
            table.add_row(*(str(row[column]) if row[column] is not None else "" for column in columns))
        console.print(table)


def print_paths(console: Console) -> None:
    table = Table(title="Caminhos")
    table.add_column("Item")
    table.add_column("Caminho")
    table.add_row("Banco", str(db_path()))
    table.add_row("Configuração", str(config_path()))
    table.add_row("Comando", str(Path.home() / ".local" / "bin" / "habits"))
    console.print(table)
