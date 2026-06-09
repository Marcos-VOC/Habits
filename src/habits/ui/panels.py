from __future__ import annotations

import sqlite3
from pathlib import Path

from rich.console import Console
from rich.table import Table

from habits import models
from habits.paths import config_path, db_path
from habits.stats import current_streak, streaks_for_habits
from habits.ui.labels import frequency_label


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
    if table.row_count == 0:
        table.add_row("-", "Nenhum hábito ativo", "-", "", "")
    console.print(table)


def print_streaks(console: Console, conn: sqlite3.Connection) -> None:
    table = Table(title="Sequências atuais")
    table.add_column("ID", justify="right")
    table.add_column("Hábito")
    table.add_column("Frequência")
    table.add_column("Sequência", justify="right")
    for item in streaks_for_habits(conn):
        table.add_row(str(item["id"]), f'{item["icon"]} {item["name"]}', frequency_label(item["frequency_type"]), str(item["streak"]))
    if table.row_count == 0:
        table.add_row("-", "Nenhum hábito ativo", "-", "-")
    console.print(table)


def print_habits(console: Console, conn: sqlite3.Connection, *, active: bool | None = True) -> None:
    table = Table(title="Hábitos")
    table.add_column("Nº", justify="right")
    table.add_column("Hábito")
    table.add_column("Cor")
    table.add_column("Frequência")
    table.add_column("Meta")
    table.add_column("Sequência", justify="right")
    for index, habit in enumerate(models.list_habits(conn, active=active), start=1):
        table.add_row(
            str(index),
            f'{habit["icon"]} {habit["name"]}',
            habit["color"],
            frequency_label(habit["frequency_type"]),
            str(habit["frequency_target"]),
            str(current_streak(conn, habit["id"])),
        )
    if table.row_count == 0:
        table.add_row("-", "Nenhum hábito encontrado", "-", "-", "-", "-")
    console.print(table)


def print_db(console: Console, conn: sqlite3.Connection) -> None:
    for table_name in ("habits", "entries"):
        rows = conn.execute(f"SELECT * FROM {table_name} ORDER BY id").fetchall()
        schema_rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()

        schema = Table(title=f"Estrutura - {table_name}", show_lines=True)
        schema.add_column("Coluna")
        schema.add_column("Tipo")
        for row in schema_rows:
            schema.add_row(row["name"], row["type"] or "-")
        console.print(schema)

        if not rows:
            console.print(f"[yellow]Nenhum registro em {table_name}.[/yellow]\n")
            continue

        columns = [row["name"] for row in schema_rows]
        for row in rows:
            record = Table(title=f"{table_name} #{row['id']}", show_lines=True)
            record.add_column("Campo")
            record.add_column("Valor")
            for column in columns:
                value = str(row[column]) if row[column] is not None else ""
                record.add_row(column, value)
            console.print(record)


def print_paths(console: Console) -> None:
    table = Table(title="Caminhos")
    table.add_column("Item")
    table.add_column("Caminho")
    table.add_row("Banco", str(db_path()))
    table.add_row("Configuração", str(config_path()))
    table.add_row("Comando", str(Path.home() / ".local" / "bin" / "habits"))
    console.print(table)


def print_habit_history(console: Console, conn: sqlite3.Connection, habit_id: int) -> None:
    habit = models.get_habit(conn, habit_id)
    table = Table(title=f'Histórico - {habit["icon"]} {habit["name"]}')
    table.add_column("Data")
    table.add_column("Duração")
    table.add_column("Nota")
    for entry in models.habit_history(conn, habit_id):
        duration = str(entry["duration_minutes"] or "")
        table.add_row(entry["date"], duration, entry["note"] or "")
    if table.row_count == 0:
        table.add_row("-", "Nenhum registro encontrado", "")
    console.print(table)


def print_guide(console: Console) -> None:
    table = Table(title="Guia de comandos")
    table.add_column("Comando")
    table.add_column("O que faz")
    table.add_row("habits", "Abre o menu interativo")
    table.add_row("habits check | registrar", "Registra um hábito de hoje")
    table.add_row("habits check treinar", "Busca um hábito por nome e registra")
    table.add_row("habits hoje | today", "Mostra o resumo do dia")
    table.add_row("habits streak | sequencia", "Mostra sequências atuais")
    table.add_row("habits historico estudar", "Mostra histórico por hábito")
    table.add_row("habits db | banco", "Mostra dados técnicos do SQLite")
    table.add_row("habits paths | caminhos", "Mostra caminhos de banco/config")
    table.add_row("Configurações > Caminhos", "Mostra caminhos dentro do menu interativo")
    table.add_row("habits help | ajuda | guia", "Mostra este guia")
    table.add_row("No menu principal", "Também aceita comandos como habits registrar Correr")
    console.print(table)
