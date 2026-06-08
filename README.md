# Habits

Habits is a personal habit tracker for the terminal, built for Fedora/Linux with Python, Rich, and SQLite.

The interface is in Portuguese, while the internal code, database, and config use English names.

## v0.1

- Interactive Rich menu.
- Create, list, and archive habits.
- Register one entry per habit per day with optional duration and note.
- Current streaks for daily, weekdays, and weekly habits.
- Quick commands with Portuguese and English aliases.
- SQLite database viewer.
- Paths viewer.
- Local user install/uninstall through `run.sh`.

## Install

```bash
./run.sh install
```

This installs the `habits` command for the current user at:

```text
~/.local/bin/habits
```

## Run

```bash
habits
habits hoje
habits today
habits check
habits registrar
habits streak
habits sequencia
habits db
habits banco
habits paths
habits caminhos
```

During development, you can run without installing:

```bash
./run.sh
./run.sh hoje
```

## Data

Habits stores user data in standard Linux user directories:

```text
~/.local/share/habits/habits.db
~/.config/habits/config.json
```

Uninstall asks whether to keep or remove these files:

```bash
./run.sh uninstall
```

## Tests

```bash
./run.sh test
```

Tests use temporary paths and do not touch your real Habits data.
