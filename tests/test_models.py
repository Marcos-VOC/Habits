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

    models.unarchive_habit(conn, habit["id"])

    assert models.list_habits(conn, active=True)[0]["id"] == habit["id"]


def test_find_habits_by_partial_name(conn):
    habit = models.create_habit(conn, "Treinar força")
    models.create_habit(conn, "Ler")

    matches = models.find_habits(conn, "treinar")

    assert [match["id"] for match in matches] == [habit["id"]]


def test_list_habits_orders_by_id(conn):
    first = models.create_habit(conn, "Z depois no alfabeto")
    second = models.create_habit(conn, "A antes no alfabeto")

    assert [habit["id"] for habit in models.list_habits(conn, active=True)] == [first["id"], second["id"]]


def test_weekly_frequency_target_cannot_exceed_week_days(conn):
    try:
        models.create_habit(conn, "Correr", frequency_type="weekly", frequency_target=9)
    except ValueError as exc:
        assert "between 1 and 7" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_update_habit_changes_editable_fields(conn):
    habit = models.create_habit(conn, "Ler", icon="📘", color="azul", daily_goal_minutes=20)

    updated = models.update_habit(
        conn,
        habit["id"],
        name="Estudar",
        icon="🧠",
        color="VERDE",
        frequency_type="weekly",
        frequency_target=3,
        daily_goal_minutes=45,
    )

    assert updated["name"] == "Estudar"
    assert updated["icon"] == "🧠"
    assert updated["color"] == "verde"
    assert updated["frequency_type"] == "weekly"
    assert updated["frequency_target"] == 3
    assert updated["daily_goal_minutes"] == 45


def test_update_habit_can_clear_daily_goal(conn):
    habit = models.create_habit(conn, "Ler", daily_goal_minutes=20)

    updated = models.update_habit(conn, habit["id"], clear_daily_goal=True)

    assert updated["daily_goal_minutes"] is None


def test_update_weekly_frequency_target_cannot_exceed_week_days(conn):
    habit = models.create_habit(conn, "Correr")

    try:
        models.update_habit(conn, habit["id"], frequency_type="weekly", frequency_target=9)
    except ValueError as exc:
        assert "between 1 and 7" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_register_entry_updates_same_day(conn):
    habit = models.create_habit(conn, "Estudar")

    first = models.register_entry(conn, habit["id"], entry_date=date(2026, 6, 8), duration_minutes="1h30", note="Python")
    second = models.register_entry(conn, habit["id"], entry_date=date(2026, 6, 8), duration_minutes="45min", note="SQL")

    assert first["id"] == second["id"]
    assert second["duration_minutes"] == 45
    assert second["note"] == "SQL"


def test_habit_history(conn):
    habit = models.create_habit(conn, "Estudar")
    models.register_entry(conn, habit["id"], entry_date=date(2026, 6, 8), duration_minutes="45min", note="SQL")

    history = models.habit_history(conn, habit["id"])

    assert history[0]["habit_name"] == "Estudar"
    assert history[0]["duration_minutes"] == 45


def test_delete_habit_removes_entries(conn):
    habit = models.create_habit(conn, "Apagar")
    models.register_entry(conn, habit["id"], entry_date=date(2026, 6, 8))

    models.delete_habit(conn, habit["id"])

    assert models.list_habits(conn, active=None) == []
    assert models.list_entries(conn) == []


def test_parse_duration_formats():
    assert models.parse_duration("") is None
    assert models.parse_duration("90") == 90
    assert models.parse_duration("90min") == 90
    assert models.parse_duration("1h") == 60
    assert models.parse_duration("1h30") == 90
    assert models.parse_duration("1h 30min") == 90
