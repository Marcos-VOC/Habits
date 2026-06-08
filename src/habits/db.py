from __future__ import annotations

import sqlite3
from pathlib import Path

from .paths import db_path, ensure_parent


SCHEMA = """
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    icon TEXT DEFAULT '⭐',
    color TEXT DEFAULT 'azul',
    daily_goal_minutes INTEGER DEFAULT NULL,
    frequency_type TEXT DEFAULT 'daily'
        CHECK (frequency_type IN ('daily', 'weekdays', 'weekly')),
    frequency_target INTEGER DEFAULT 1,
    streak_alert_minimum INTEGER DEFAULT NULL,
    active INTEGER DEFAULT 1,
    created_at DATE DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL REFERENCES habits(id),
    date DATE NOT NULL,
    done INTEGER DEFAULT 1,
    duration_minutes INTEGER DEFAULT NULL,
    note TEXT DEFAULT NULL,
    UNIQUE(habit_id, date)
);
"""


def connect(path: Path | None = None) -> sqlite3.Connection:
    final_path = path or db_path()
    ensure_parent(final_path)
    conn = sqlite3.connect(final_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection | None = None) -> None:
    owns_connection = conn is None
    connection = conn or connect()
    try:
        connection.executescript(SCHEMA)
        connection.commit()
    finally:
        if owns_connection:
            connection.close()
