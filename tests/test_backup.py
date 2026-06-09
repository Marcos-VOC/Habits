from __future__ import annotations

import csv
import json

from habits import backup, models


def test_export_json_writes_habits_and_entries(conn, monkeypatch, tmp_path):
    monkeypatch.setenv("HABITS_BACKUP_DIR", str(tmp_path))
    monkeypatch.setenv("HABITS_CONFIG_PATH", str(tmp_path / "config.json"))
    habit = models.create_habit(conn, "Ler")
    models.register_entry(conn, habit["id"])

    path = backup.export_json(conn)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert path.parent == tmp_path
    assert payload["habits"][0]["name"] == "Ler"
    assert payload["entries"][0]["habit_id"] == habit["id"]


def test_export_csv_writes_both_tables(conn, monkeypatch, tmp_path):
    monkeypatch.setenv("HABITS_BACKUP_DIR", str(tmp_path))
    habit = models.create_habit(conn, "Ler")
    models.register_entry(conn, habit["id"])

    folder = backup.export_csv(conn)

    assert (folder / "habits.csv").exists()
    assert (folder / "entries.csv").exists()
    habits_rows = list(csv.DictReader((folder / "habits.csv").open(encoding="utf-8")))
    entries_rows = list(csv.DictReader((folder / "entries.csv").open(encoding="utf-8")))
    assert habits_rows[0]["name"] == "Ler"
    assert entries_rows[0]["habit_id"] == str(habit["id"])


def test_complete_backup_copies_existing_files(monkeypatch, tmp_path):
    db_path = tmp_path / "habits.db"
    config_path = tmp_path / "config.json"
    db_path.write_text("db", encoding="utf-8")
    config_path.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("HABITS_DB_PATH", str(db_path))
    monkeypatch.setenv("HABITS_CONFIG_PATH", str(config_path))
    monkeypatch.setenv("HABITS_BACKUP_DIR", str(tmp_path / "backups"))

    folder = backup.create_complete_backup()

    assert (folder / "habits.db").read_text(encoding="utf-8") == "db"
    assert (folder / "config.json").read_text(encoding="utf-8") == "{}"
