from __future__ import annotations

import re
import sqlite3
from datetime import date
from typing import Any

from .palette import normalize_color


FREQUENCY_ALIASES = {
    "daily": "daily",
    "diario": "daily",
    "diário": "daily",
    "todos": "daily",
    "weekdays": "weekdays",
    "dias_uteis": "weekdays",
    "dias úteis": "weekdays",
    "segunda a sexta": "weekdays",
    "weekly": "weekly",
    "x_por_semana": "weekly",
    "semana": "weekly",
}


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def normalize_frequency(value: str | None) -> str:
    if not value:
        return "daily"
    return FREQUENCY_ALIASES.get(value.strip().lower(), "daily")


def parse_duration(value: str | None) -> int | None:
    if value is None:
        return None
    text = value.strip().lower()
    if not text:
        return None
    if text.isdigit():
        return int(text)

    hours = 0
    minutes = 0
    hour_match = re.search(r"(\d+)\s*h", text)
    minute_match = re.search(r"(\d+)\s*(m|min)", text)
    if hour_match:
        hours = int(hour_match.group(1))
        compact_minutes = re.search(r"\d+\s*h\s*(\d+)$", text)
        if compact_minutes:
            minutes = int(compact_minutes.group(1))
    if minute_match:
        minutes = int(minute_match.group(1))
    if hour_match or minute_match:
        return hours * 60 + minutes

    raise ValueError("duration must be like 90, 90min, 1h or 1h30")


def create_habit(
    conn: sqlite3.Connection,
    name: str,
    *,
    icon: str | None = None,
    color: str | None = None,
    daily_goal_minutes: int | None = None,
    frequency_type: str | None = None,
    frequency_target: int = 1,
    streak_alert_minimum: int | None = None,
) -> dict[str, Any]:
    if not name.strip():
        raise ValueError("habit name is required")
    frequency = normalize_frequency(frequency_type)
    target = max(1, int(frequency_target or 1))
    if frequency == "weekly" and target > 7:
        raise ValueError("weekly frequency target must be between 1 and 7")
    cursor = conn.execute(
        """
        INSERT INTO habits (
            name, icon, color, daily_goal_minutes, frequency_type,
            frequency_target, streak_alert_minimum
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name.strip(),
            (icon or "⭐").strip() or "⭐",
            normalize_color(color),
            daily_goal_minutes,
            frequency,
            target,
            streak_alert_minimum,
        ),
    )
    conn.commit()
    return get_habit(conn, cursor.lastrowid)


def get_habit(conn: sqlite3.Connection, habit_id: int) -> dict[str, Any]:
    row = conn.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
    if row is None:
        raise ValueError(f"habit not found: {habit_id}")
    return row_to_dict(row)


def list_habits(conn: sqlite3.Connection, *, active: bool | None = True) -> list[dict[str, Any]]:
    if active is None:
        rows = conn.execute("SELECT * FROM habits ORDER BY active DESC, id ASC").fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM habits WHERE active = ? ORDER BY id ASC",
            (1 if active else 0,),
        ).fetchall()
    return [row_to_dict(row) for row in rows]


def archive_habit(conn: sqlite3.Connection, habit_id: int) -> None:
    conn.execute("UPDATE habits SET active = 0 WHERE id = ?", (habit_id,))
    conn.commit()


def unarchive_habit(conn: sqlite3.Connection, habit_id: int) -> None:
    conn.execute("UPDATE habits SET active = 1 WHERE id = ?", (habit_id,))
    conn.commit()


def find_habits(conn: sqlite3.Connection, query: str, *, active: bool | None = True) -> list[dict[str, Any]]:
    clean_query = query.strip()
    if not clean_query:
        return []
    params: list[Any] = []
    where = "WHERE name LIKE ? COLLATE NOCASE"
    params.append(f"%{clean_query}%")
    if active is not None:
        where += " AND active = ?"
        params.append(1 if active else 0)
    rows = conn.execute(
        f"SELECT * FROM habits {where} ORDER BY name COLLATE NOCASE",
        params,
    ).fetchall()
    return [row_to_dict(row) for row in rows]


def register_entry(
    conn: sqlite3.Connection,
    habit_id: int,
    *,
    entry_date: date | None = None,
    duration_minutes: int | str | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    final_date = (entry_date or date.today()).isoformat()
    duration = parse_duration(duration_minutes) if isinstance(duration_minutes, str) else duration_minutes
    clean_note = note.strip() if isinstance(note, str) and note.strip() else None
    conn.execute(
        """
        INSERT INTO entries (habit_id, date, done, duration_minutes, note)
        VALUES (?, ?, 1, ?, ?)
        ON CONFLICT(habit_id, date) DO UPDATE SET
            done = excluded.done,
            duration_minutes = excluded.duration_minutes,
            note = excluded.note
        """,
        (habit_id, final_date, duration, clean_note),
    )
    conn.commit()
    return get_entry(conn, habit_id, final_date)


def get_entry(conn: sqlite3.Connection, habit_id: int, entry_date: str) -> dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM entries WHERE habit_id = ? AND date = ?",
        (habit_id, entry_date),
    ).fetchone()
    if row is None:
        raise ValueError("entry not found")
    return row_to_dict(row)


def entry_exists(conn: sqlite3.Connection, habit_id: int, entry_date: date | None = None) -> bool:
    final_date = (entry_date or date.today()).isoformat()
    row = conn.execute(
        "SELECT 1 FROM entries WHERE habit_id = ? AND date = ?",
        (habit_id, final_date),
    ).fetchone()
    return row is not None


def list_entries(conn: sqlite3.Connection, habit_id: int | None = None) -> list[dict[str, Any]]:
    if habit_id is None:
        rows = conn.execute("SELECT * FROM entries ORDER BY date DESC, habit_id").fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM entries WHERE habit_id = ? ORDER BY date DESC",
            (habit_id,),
        ).fetchall()
    return [row_to_dict(row) for row in rows]


def habit_history(conn: sqlite3.Connection, habit_id: int) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT e.*, h.name AS habit_name, h.icon AS habit_icon
        FROM entries e
        JOIN habits h ON h.id = e.habit_id
        WHERE e.habit_id = ?
        ORDER BY e.date DESC
        """,
        (habit_id,),
    ).fetchall()
    return [row_to_dict(row) for row in rows]


def today_summary(conn: sqlite3.Connection, today: date | None = None) -> list[dict[str, Any]]:
    final_date = (today or date.today()).isoformat()
    rows = conn.execute(
        """
        SELECT h.*, e.id AS entry_id, e.duration_minutes, e.note
        FROM habits h
        LEFT JOIN entries e ON e.habit_id = h.id AND e.date = ?
        WHERE h.active = 1
        ORDER BY h.name COLLATE NOCASE
        """,
        (final_date,),
    ).fetchall()
    summary = []
    for row in rows:
        item = row_to_dict(row)
        item["done_today"] = item["entry_id"] is not None
        summary.append(item)
    return summary
