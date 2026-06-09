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
- First-steps menu when no habits exist yet.
- Dynamic menus for data-state-dependent actions.
- Create, list, archive, unarchive, and delete habits.
- Register one entry per habit per day with optional duration and note.
- Current streak calculation.
- Quick commands with PT/EN aliases.
- Direct commands by habit name.
- Habit-specific history view.
- Database viewer for technical inspection.
- Command guide.
- Paths viewer inside settings and as a direct command.
- Basic config management.
- Basic tests from the beginning.

## v0.2 Scope

- Edit habit name, icon, color, frequency, and daily goal from the interactive manager.
- Icon picker organized by numbered categories, with manual emoji entry still available.
- Backup/export flow inside settings:
  - Complete backup copies the database and config.
  - JSON export includes config, habits, and entries.
  - CSV export writes `habits.csv` and `entries.csv`.
- Backup/export files default to `~/Downloads/habits-backups/`.
- Tests and development may override backup/export output with `HABITS_BACKUP_DIR`.

## Deferred

- Matplotlib charts.
- GTK 4/libadwaita UI.
- Advanced alerts.
- Advanced statistics.

## Behavior Decisions

- Week starts on Monday and ends on Sunday.
- `weekdays` means Monday to Friday only.
- Saturday and Sunday are valid for daily and weekly-frequency habits.
- If an entry already exists for today, the app asks whether to update it.
- Archiving a habit never deletes its history.
- Terminal screens should clear before rendering new menu content.
- The Habits banner should appear on all interactive menu screens, not only the home screen.
- The banner must degrade gracefully on narrower terminal widths.
- User-facing frequency labels must be in Portuguese.
- Empty habit ID prompts should cancel and return toward the main menu.
- The config should not include a greeting toggle.
- Empty or invalid user input must be handled with friendly messages, never raw tracebacks.
- Pause/return prompts should use the same bordered input style as menu choices.
- Empty dependent screens should render a friendly warning and a bordered Enter-to-return prompt.
- When the database has no habits at all, the interactive menu should show a reduced first-steps menu with only actions that make sense.
- Menus should hide actions that are not currently possible when there is a clear data-state reason, such as no active habits or no archived habits.
- Archiving must have a matching unarchive flow.
- Deleting a habit is definitive, removes its entries, and must require strong confirmation by exact habit name plus `S`/`N`.
- Habit-specific history is a user-facing screen; `db` remains a technical/debug view.
- Habit history in the interactive UI should show selection and result as separate screens; returning from the result goes back to history selection.
- The main menu should show `Registrar hábito` before `Menu do dia`.
- Habit history should live under `Gerenciar hábitos`, not as a top-level main-menu option.
- Paths should be displayed directly inside `Configurações`, not as a selectable option or separate top-level interactive menu option.
- Database viewer should remain available as a direct technical command, not as a regular interactive menu item.
- Icon input should show suggested emoji but still accept any short emoji/character the terminal can render.
- Direct commands may accept habit-name arguments, e.g. `habits check treinar` and `habits historico estudar`.
- If a direct habit-name search matches multiple habits, the user should choose from the matches.
- The main menu input may also accept direct command text, e.g. `habits registrar Correr`, not only numeric choices.
- Confirmations must use Portuguese `S`/`N`, not English `y/n`.
- Weekly frequency targets must be limited to 1-7 because the current data model stores at most one entry per habit per date.
- `daily` means one expected completion per calendar day, not multiple occurrences in a day.
- Color input should be case-insensitive.
- User-facing validation errors should be Portuguese.
- Invalid menu choices should not keep stacking prompt boxes; clear/re-render around the warning.
- Sequential boxed inputs should be transient: after Enter, the active input box disappears and a simple confirmation line remains before the next input appears.
- In habit creation, boxed inputs such as frequency and weekly target should also be transient; only the current active input keeps a green border.
- User-facing habit selection should use sequential visual numbers (`Nº`) mapped internally to stable database IDs. Real IDs are technical and should remain visible only in database/debug views.
- Editing a habit changes future presentation and rules, but does not rewrite old entries.
- Editing a frequency should ask for a new weekly target only when the new frequency is `weekly`.
- Empty daily goal during editing means the daily goal should be removed.
- Backup/export belongs inside settings, while the paths table remains visible directly on the settings screen.
