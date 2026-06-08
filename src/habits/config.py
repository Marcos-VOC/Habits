from __future__ import annotations

import json
from typing import Any

from .paths import config_path, ensure_parent
from .palette import normalize_color


DEFAULT_CONFIG = {
    "streak_alert_minimum": 5,
    "default_color": "azul",
    "user_name": "Marcos",
    "show_greeting": True,
    "terminal_theme": "escuro",
}


def _validate(raw: dict[str, Any]) -> dict[str, Any]:
    config = dict(DEFAULT_CONFIG)

    if isinstance(raw.get("streak_alert_minimum"), int) and raw["streak_alert_minimum"] >= 0:
        config["streak_alert_minimum"] = raw["streak_alert_minimum"]

    if isinstance(raw.get("default_color"), str):
        config["default_color"] = normalize_color(raw["default_color"])

    if isinstance(raw.get("user_name"), str) and raw["user_name"].strip():
        config["user_name"] = raw["user_name"].strip()

    if isinstance(raw.get("show_greeting"), bool):
        config["show_greeting"] = raw["show_greeting"]

    if raw.get("terminal_theme") in {"escuro", "claro"}:
        config["terminal_theme"] = raw["terminal_theme"]

    return config


def load_config() -> dict[str, Any]:
    path = config_path()
    ensure_parent(path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("config root must be an object")
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        config = dict(DEFAULT_CONFIG)
        save_config(config)
        return config

    config = _validate(raw)
    if config != raw:
        save_config(config)
    return config


def save_config(config: dict[str, Any]) -> None:
    path = config_path()
    ensure_parent(path)
    path.write_text(json.dumps(_validate(config), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def reset_config() -> dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    save_config(config)
    return config
