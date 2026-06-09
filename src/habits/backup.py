from __future__ import annotations

import csv
import json
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import load_config
from .models import list_entries, list_habits
from .paths import config_path, db_path


def backup_root() -> Path:
    override = os.environ.get("HABITS_BACKUP_DIR")
    if override:
        return Path(override).expanduser()
    return Path.home() / "Downloads" / "habits-backups"


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d-%H%M%S")


def create_complete_backup() -> Path:
    destination = backup_root() / f"habits-backup-{timestamp()}"
    destination.mkdir(parents=True, exist_ok=True)

    database = db_path()
    if database.exists():
        shutil.copy2(database, destination / "habits.db")

    config = config_path()
    if config.exists():
        shutil.copy2(config, destination / "config.json")

    return destination


def _export_payload(conn: sqlite3.Connection) -> dict[str, Any]:
    return {
        "exported_at": datetime.now().isoformat(timespec="seconds"),
        "config": load_config(),
        "habits": list_habits(conn, active=None),
        "entries": list_entries(conn),
    }


def export_json(conn: sqlite3.Connection) -> Path:
    backup_root().mkdir(parents=True, exist_ok=True)
    destination = backup_root() / f"habits-export-{timestamp()}.json"
    destination.write_text(
        json.dumps(_export_payload(conn), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destination


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        if rows:
            writer.writerows(rows)


def export_csv(conn: sqlite3.Connection) -> Path:
    destination = backup_root() / f"habits-export-{timestamp()}"
    destination.mkdir(parents=True, exist_ok=True)
    _write_csv(
        destination / "habits.csv",
        list_habits(conn, active=None),
        [
            "id",
            "name",
            "icon",
            "color",
            "daily_goal_minutes",
            "frequency_type",
            "frequency_target",
            "streak_alert_minimum",
            "active",
            "created_at",
        ],
    )
    _write_csv(
        destination / "entries.csv",
        list_entries(conn),
        ["id", "habit_id", "date", "done", "duration_minutes", "note"],
    )
    return destination
