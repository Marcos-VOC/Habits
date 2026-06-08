from __future__ import annotations

from datetime import date

from habits import models
from habits.stats import current_streak


def test_daily_streak(conn):
    habit = models.create_habit(conn, "Ler", frequency_type="daily")
    models.register_entry(conn, habit["id"], entry_date=date(2026, 6, 6))
    models.register_entry(conn, habit["id"], entry_date=date(2026, 6, 7))
    models.register_entry(conn, habit["id"], entry_date=date(2026, 6, 8))

    assert current_streak(conn, habit["id"], today=date(2026, 6, 8)) == 3


def test_weekdays_streak_skips_weekend(conn):
    habit = models.create_habit(conn, "Trabalho", frequency_type="weekdays")
    models.register_entry(conn, habit["id"], entry_date=date(2026, 6, 5))
    models.register_entry(conn, habit["id"], entry_date=date(2026, 6, 8))

    assert current_streak(conn, habit["id"], today=date(2026, 6, 8)) == 2


def test_weekly_streak(conn):
    habit = models.create_habit(conn, "Academia", frequency_type="weekly", frequency_target=3)
    for day in (1, 3, 5, 8, 10, 12):
        models.register_entry(conn, habit["id"], entry_date=date(2026, 6, day))

    assert current_streak(conn, habit["id"], today=date(2026, 6, 12)) == 2
