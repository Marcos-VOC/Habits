from __future__ import annotations

import os
from pathlib import Path


APP_NAME = "habits"


def data_dir() -> Path:
    return Path.home() / ".local" / "share" / APP_NAME


def config_dir() -> Path:
    return Path.home() / ".config" / APP_NAME


def db_path() -> Path:
    override = os.environ.get("HABITS_DB_PATH")
    if override:
        return Path(override).expanduser()
    return data_dir() / "habits.db"


def config_path() -> Path:
    override = os.environ.get("HABITS_CONFIG_PATH")
    if override:
        return Path(override).expanduser()
    return config_dir() / "config.json"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
