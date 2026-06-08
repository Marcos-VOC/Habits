# Habits - Project Context

## Product

- Project/product name: Habits.
- Main command: `habits`.
- User interface language: Portuguese.
- Internal code, database tables/columns, and config keys: English.
- CLI supports Portuguese and English aliases for subcommands.

## Target

- Fedora Linux with GNOME.
- Python 3 terminal app using Rich.
- SQLite via Python standard library `sqlite3`.
- Offline at runtime, no sudo, no background processes.

## Data Locations

- User database: `~/.local/share/habits/habits.db`.
- User config: `~/.config/habits/config.json`.
- Tests and development may override paths with:
  - `HABITS_DB_PATH`
  - `HABITS_CONFIG_PATH`

## Install/Uninstall

- `./run.sh install` installs the app for the current user.
- `./run.sh uninstall` removes the user command and asks whether to keep or remove user data.
- Reinstalling must reuse existing user data when kept.

## v0.1 Scope

- Rich CLI and interactive menu.
- Welcome screen.
- Create, list, and archive habits.
- Register one entry per habit per day with optional duration and note.
- Current streak calculation.
- Quick commands with PT/EN aliases.
- Database viewer.
- Paths viewer.
- Basic config management.
- Basic tests from the beginning.

## Deferred

- Matplotlib charts.
- GTK 4/libadwaita UI.
- Advanced alerts.
- Advanced statistics.
- Backup/export.
- Visual mascot/icons.

## Behavior Decisions

- Week starts on Monday and ends on Sunday.
- `weekdays` means Monday to Friday only.
- Saturday and Sunday are valid for daily and weekly-frequency habits.
- If an entry already exists for today, the app asks whether to update it.
- Archiving a habit never deletes its history.
