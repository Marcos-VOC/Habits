# Habits

Habits is a personal habit tracker for the terminal, built for Fedora/Linux with Python, Rich, and SQLite.

The user interface is in Portuguese. Internal code, database tables/columns, and config keys use English names.

## Features

- Interactive terminal menu with Rich.
- First-steps menu when no habits exist yet.
- Dynamic menus that hide actions that cannot be used in the current data state.
- Create, edit, list, archive, unarchive, and delete habits.
- Icon picker by category, while still allowing any emoji supported by the terminal.
- Register one entry per habit per day with optional duration and note.
- Current streaks for daily, weekdays, and weekly habits.
- Habit-specific history view.
- Backup/export flow in settings, with complete backup, JSON export, and CSV export.
- Quick commands with Portuguese and English aliases.
- Direct commands by habit name, such as `habits check treinar`.
- SQLite technical viewer through `habits db` or `habits banco`.
- Command guide through `habits guia`.
- Paths are shown directly in the settings menu and through `habits paths`.
- Local user install/uninstall through `run.sh`.

## Important Rules

- `Todos os dias` means one expected completion per calendar day.
- `Segunda a sexta` ignores Saturday and Sunday for streak calculation.
- `X vezes por semana` accepts a weekly target from 1 to 7.
- Habits stores at most one entry per habit per date.
- Confirmations use `S`/`N`.
- Deleting a habit is permanent and also removes its history.
- User-facing habit lists use sequential visual numbers; SQLite IDs remain stable internally.
- Color input is case-insensitive, so `azul`, `Azul`, and `AZUL` resolve to the same color.

## Install

```bash
./run.sh install
```

This installs the `habits` command for the current user at:

```text
~/.local/bin/habits
```

Uninstall asks whether to keep or remove user data:

```bash
./run.sh uninstall
```

## Run

During development, you can run without installing:

```bash
./run.sh
./run.sh hoje
```

After installing:

```bash
habits
habits hoje
habits today
habits check
habits registrar
habits check treinar
habits streak
habits sequencia
habits history
habits historico
habits historico estudar
habits guia
habits comandos
habits paths
habits caminhos
habits db
habits banco
```

## Data

Habits stores user data in standard Linux user directories:

```text
~/.local/share/habits/habits.db
~/.config/habits/config.json
```

Tests and development may override those paths:

```bash
HABITS_DB_PATH=/tmp/habits-test.db HABITS_CONFIG_PATH=/tmp/habits-config.json ./run.sh
```

Backups and exports are saved by default under:

```text
~/Downloads/habits-backups/
```

Tests and development may override that directory:

```bash
HABITS_BACKUP_DIR=/tmp/habits-backups ./run.sh
```

## Development

Runtime dependency:

```text
rich
```

Development/test dependency:

```text
pytest
```

Run tests:

```bash
./run.sh test
```

Tests use temporary paths and do not touch your real Habits data.

## Project Layout

```text
src/habits/
  main.py          CLI routing
  db.py            SQLite connection and schema
  models.py        CRUD and data access
  stats.py         streak calculations
  backup.py        backup and export helpers
  config.py        user config
  palette.py       color palette
  paths.py         data/config paths
  ui/              Rich terminal UI
tests/             pytest suite
```

## Roadmap

- Add advanced statistics.
- Add advanced alerts.
- Add charts.
- Add GTK/libadwaita UI later.
