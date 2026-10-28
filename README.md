# Liquid Calendar · Beta

A local desktop calendar and task planner for **Fedora Linux / KDE Plasma 6**. English interface, no account required.

**Current beta: 0.2.0-beta.1** · **GPL-3.0-or-later**

[Download 0.2.0 Beta 1](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.2.0-beta.1) · [Release notes](RELEASE_NOTES.md) · [Known issues](KNOWN_ISSUES.md) · [Roadmap](ROADMAP.md)

![Today view with synthetic example data](docs/screenshots/today.png)

## Features

- Today overview, 24-hour weekly timeline, month and 7/14/30-day agenda views.
- Undated tasks with optional scheduling, categories, filters and sorting. Complete individual occurrences of repeating tasks while keeping future repetitions open.
- Task priorities, editable checklists and projects, with combined filters and sorting.
- Search across years using titles, projects, checklist steps, locations, notes, dates and partial month/day names.
- Repeats, individual occurrences, reminders and available-time suggestions.
- Conflict-aware local storage, undo, daily backups and optional Plasma widget.
- JSON backup/import and ICS event export.

![Task organization with synthetic example data](docs/screenshots/tasks.png)

The second beta milestone adds task organization. Released **28 October 2026**. See [release notes](RELEASE_NOTES.md), [audit results](docs/BUG_AUDIT_0.2.0.md) and the [release record](docs/RELEASE_0.2.0.md).

## Roadmap

See the [roadmap](ROADMAP.md) for the ten beta milestones, planned features and bug-fix versioning rules.

## Install

Requirements: Fedora/KDE Plasma 6, **Python 3.10–3.14**, venv/pip support, network access to PyPI and the system Qt platform libraries. `notify-send` is needed for notifications. Other systems are not validated.

Download an archive from the [0.2.0 Beta 1 release](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.2.0-beta.1), extract it and open a terminal in its folder:

```bash
python3 installieren.py
```

To also install the optional Plasma widget:

```bash
python3 installieren.py --with-widget
```

No sudo is needed. The installer creates a per-user virtual environment with pinned Qt dependencies and an application-menu entry **Liquid Calendar Beta**. It backs up existing program files and never opens or modifies the event database. The download contains source code, not bundled third-party runtime binaries.

After an update, quit the old app using **Ctrl+Q** and reopen it. Add **Liquid Glass Calendar (Beta)** through Plasma's widget picker if installed. If an old widget is active, use **Connect** when prompted; this briefly reloads the desktop and panels.

**Beta scope:** Fedora/KDE Plasma is the target. See [known limitations](KNOWN_ISSUES.md) and [testing details](TESTING.md) for supported behavior and validation scope.

## Use

Create **+ Event** or **+ Task**. Tasks are undated by default. **Schedule in calendar** or **Find time** assigns a date explicitly; suggestions cover 09:00–18:00. More options reveals categories, repeats, reminders, locations and notes. Dragging a repeating event moves only that occurrence; use **Series** to edit the whole series.

In **+ Task**, choose No priority, Low, Medium or High, enter an optional project and add checklist steps. Tasks remain undated unless explicitly scheduled. The Tasks view combines project, priority, category, status, schedule and text filters; **Reset** clears them. Use **Sort** for priority or project ordering. The checklist counter expands inline steps. Completing all steps does not automatically complete the task.

Projects are created by assigning a name to a task. Project menus show completed/total task records, including detached occurrences. Select a project and use **Edit project** to rename it, merge it with an existing name, or clear its assignments without deleting tasks. App-wide Undo covers these edits. Project names are case-sensitive and limited to 80 characters; `*` is reserved. Each task supports up to 100 checklist steps.

For repeating tasks, inline checklist clicks affect only that occurrence; future repetitions keep their original checklist. **Series** edits the checklist template for the whole series.

Search `today`, `tomorrow`, `day after tomorrow`, `wed`, `nov`, `2027-03-15` or `15.03.2027`. Dates use English names and 24-hour time. German query aliases remain supported, but there is no language selector. Slash-based US dates are not supported.

When completing a repeating task, only the selected occurrence is completed. You can reopen that occurrence without creating a duplicate. If an older beta marked a whole series completed, explicitly reopen that legacy series to make future occurrences available again. Updating does not automatically rewrite stored completion states.

Reminders require the app to be open or running in the tray. Closing the window may keep it running. **Ctrl+Q** fully quits. Optional login startup is disabled by default.

- **Ctrl+N:** new event
- **Ctrl+F:** search
- **Ctrl+Z:** undo last change
- **Ctrl+Q:** quit app and reminders

## Data and privacy

No cloud synchronization, account sign-in or analytics are implemented. Data stays local. The app shares the companion widget's SQLite database at:

```text
~/.local/share/plasmashell/QML/OfflineStorage/Databases/dd9450f249be1bf7e7f3854d39b8b74b.sqlite
```

Program files are installed under `~/.local/share/liquid-glass-planner/`. Daily data backups are kept in its `backups/` directory (latest 14 daily files). Program-update backups are stored separately within that directory. Back up important data before beta use. JSON preserves tasks and metadata; ICS exports calendar events only. Import adds new IDs without replacing existing IDs.

## Develop

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./launch.sh --smoke-test
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
```

Use `--smoke-test` or `--database /path/to/a/test.sqlite` for development. Do not run against a personal database. See [TESTING.md](TESTING.md), [CONTRIBUTING.md](CONTRIBUTING.md) and [THIRD_PARTY.md](THIRD_PARTY.md).

## License

Copyright © 2026 Jonas. Project source and assets are licensed under **GNU GPL version 3 or later**, without warranty. See [LICENSE](LICENSE) and [NOTICE](NOTICE). External dependencies retain their own licenses; see [THIRD_PARTY.md](THIRD_PARTY.md).
