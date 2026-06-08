from __future__ import annotations

from datetime import date

from habits import models


def test_create_archive_and_list_habit(conn):
    habit = models.create_habit(conn, "Ler", icon="📘", color="verde")

    assert habit["name"] == "Ler"
    assert models.list_habits(conn, active=True)[0]["id"] == habit["id"]

    models.archive_habit(conn, habit["id"])

    assert models.list_habits(conn, active=True) == []
    assert models.list_habits(conn, active=False)[0]["id"] == habit["id"]


def test_register_entry_updates_same_day(conn):
    habit = models.create_habit(conn, "Estudar")

    first = models.register_entry(conn, habit["id"], entry_date=date(2026, 6, 8), duration_minutes="1h30", note="Python")
    second = models.register_entry(conn, habit["id"], entry_date=date(2026, 6, 8), duration_minutes="45min", note="SQL")

    assert first["id"] == second["id"]
    assert second["duration_minutes"] == 45
    assert second["note"] == "SQL"


def test_parse_duration_formats():
    assert models.parse_duration("") is None
    assert models.parse_duration("90") == 90
    assert models.parse_duration("90min") == 90
    assert models.parse_duration("1h") == 60
    assert models.parse_duration("1h30") == 90
    assert models.parse_duration("1h 30min") == 90
