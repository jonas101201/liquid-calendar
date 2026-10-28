# Liquid Calendar 0.2.0 Beta 1 — release preparation

Planned for **29 October 2026, 12:00 Europe/Berlin**. This release has not been published yet. English interface, Fedora/KDE Plasma, GPL-3.0-or-later.

## Task organization

- Choose no, low, medium or high priority; filter and sort tasks by priority.
- Add, edit, remove and complete up to 100 checklist steps per task. Expand progress directly in the Tasks view.
- Organize tasks into named projects. Combine project, priority, status, category and scheduling filters. Project menus display completed/total task records.
- Rename or merge projects, or clear their assignments while preserving every task. Undo restores the previous state.
- Search project names and checklist text across all dates, alongside titles, locations and notes.
- Repeating-task inline checklist progress belongs to the selected occurrence. Future occurrences keep the template's state. Marking all steps complete does not automatically complete the parent task.

## Install or update

Extract the source archive and run `python3 installieren.py`. Use `--with-widget` for a new optional widget. The installer also updates an already installed widget. Quit the old app with **Ctrl+Q**, then reopen it. Reload the desktop widget when convenient to use its new task editor.

New task details are optional fields in the existing local records, preserved by JSON backup/import. No existing entries are automatically rewritten; no database migration is required. Both app and widget support the fields. Keep a JSON backup before testing a beta.

Reminders still require the app or tray process. ICS exports events only; cloud sync and ICS import remain future milestones. See [known issues](KNOWN_ISSUES.md).

## Verification

The preparation is covered by 77 Python tests, seven JavaScript suites, real offscreen QML editor interactions and a smoke launch. Hosted CI must pass for the final release commit before publication. Fresh-account installation validation remains excluded at the maintainer's request. See [TESTING.md](TESTING.md) and the [release checklist](docs/RELEASE_0.2.0.md).
