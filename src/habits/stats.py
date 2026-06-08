from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from typing import Any


def _done_dates(conn: sqlite3.Connection, habit_id: int) -> set[date]:
    rows = conn.execute(
        "SELECT date FROM entries WHERE habit_id = ? AND done = 1",
        (habit_id,),
    ).fetchall()
    return {date.fromisoformat(row["date"]) for row in rows}


def _habit(conn: sqlite3.Connection, habit_id: int) -> dict[str, Any]:
    row = conn.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
    if row is None:
        raise ValueError(f"habit not found: {habit_id}")
    return dict(row)


def _previous_day(day: date, weekdays_only: bool) -> date:
    current = day - timedelta(days=1)
    if weekdays_only:
        while current.weekday() >= 5:
            current -= timedelta(days=1)
    return current


def daily_streak(conn: sqlite3.Connection, habit_id: int, *, today: date | None = None, weekdays_only: bool = False) -> int:
    done = _done_dates(conn, habit_id)
    current = today or date.today()
    if weekdays_only and current.weekday() >= 5:
        while current.weekday() >= 5:
            current -= timedelta(days=1)

    streak = 0
    while current in done:
        streak += 1
        current = _previous_day(current, weekdays_only)
    return streak


def _week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())


def _week_count(conn: sqlite3.Connection, habit_id: int, start: date) -> int:
    end = start + timedelta(days=6)
    row = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM entries
        WHERE habit_id = ? AND done = 1 AND date BETWEEN ? AND ?
        """,
        (habit_id, start.isoformat(), end.isoformat()),
    ).fetchone()
    return int(row["total"])


def weekly_streak(conn: sqlite3.Connection, habit_id: int, *, today: date | None = None) -> int:
    habit = _habit(conn, habit_id)
    target = max(1, int(habit["frequency_target"] or 1))
    current_week = _week_start(today or date.today())

    if _week_count(conn, habit_id, current_week) < target:
        current_week -= timedelta(days=7)

    streak = 0
    while _week_count(conn, habit_id, current_week) >= target:
        streak += 1
        current_week -= timedelta(days=7)
    return streak


def current_streak(conn: sqlite3.Connection, habit_id: int, *, today: date | None = None) -> int:
    habit = _habit(conn, habit_id)
    frequency = habit["frequency_type"]
    if frequency == "weekdays":
        return daily_streak(conn, habit_id, today=today, weekdays_only=True)
    if frequency == "weekly":
        return weekly_streak(conn, habit_id, today=today)
    return daily_streak(conn, habit_id, today=today)


def streaks_for_habits(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute("SELECT * FROM habits WHERE active = 1 ORDER BY name COLLATE NOCASE").fetchall()
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "icon": row["icon"],
            "frequency_type": row["frequency_type"],
            "streak": current_streak(conn, row["id"]),
        }
        for row in rows
    ]
