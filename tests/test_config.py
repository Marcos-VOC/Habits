from __future__ import annotations

import json

from habits.config import DEFAULT_CONFIG, load_config


def test_load_config_creates_default(monkeypatch, tmp_path):
    path = tmp_path / "config.json"
    monkeypatch.setenv("HABITS_CONFIG_PATH", str(path))

    config = load_config()

    assert config == DEFAULT_CONFIG
    assert json.loads(path.read_text(encoding="utf-8")) == DEFAULT_CONFIG


def test_load_config_recovers_corrupt_file(monkeypatch, tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{broken", encoding="utf-8")
    monkeypatch.setenv("HABITS_CONFIG_PATH", str(path))

    config = load_config()

    assert config == DEFAULT_CONFIG


def test_load_config_removes_obsolete_greeting_option(monkeypatch, tmp_path):
    path = tmp_path / "config.json"
    path.write_text(
        '{"user_name": "Marcos", "show_greeting": false, "default_color": "verde"}',
        encoding="utf-8",
    )
    monkeypatch.setenv("HABITS_CONFIG_PATH", str(path))

    config = load_config()

    assert "show_greeting" not in config
    assert config["default_color"] == "verde"
