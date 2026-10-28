# Liquid Calendar 0.2.0 Beta 1

Released **28 October 2026**. [Release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.2.0-beta.1). English interface, Fedora/KDE Plasma, GPL-3.0-or-later.

## Task organization

- Choose no, low, medium or high priority; filter and sort tasks by priority.
- Add, edit, remove and complete up to 100 checklist steps per task. Expand progress directly in the Tasks view.
- Organize tasks into named projects. Combine project, priority, status, category and scheduling filters. Project menus display completed/total task records.
- Rename or merge projects, or clear their assignments while preserving every task. Undo restores the previous state.
- Search project names and checklist text across all dates, alongside titles, locations and notes.
- Repeating-task inline checklist progress belongs to the selected occurrence. Future occurrences keep the template's state. Marking all steps complete does not automatically complete the parent task.

## Corrections included in the preparation

- Typed checklist steps and editor checkboxes are saved correctly; adding another step keeps earlier input.
- Expanded checklists stay open after a click, including recurring-occurrence edits.
- Undo after renaming or clearing a project restores the appropriate filter.
- Parallel changes to project membership reject the rename atomically; refresh and retry includes the new tasks.
- App and widget agree on Unicode character limits, and valid emoji text survives editing and duplication.
- Project summaries aggregate tasks in one pass to avoid slowdowns with many projects.

## Install or update

Extract the source archive and run `python3 installieren.py`. Use `--with-widget` for a new optional widget. The installer also updates an already installed widget. Quit the old app with **Ctrl+Q**, then reopen it. Reload the desktop widget when convenient to use its new task editor.

New task details are optional fields in the existing local records, preserved by JSON backup/import. No existing entries are automatically rewritten; no database migration is required. Both app and widget support the fields. Keep a JSON backup before testing a beta.

Reminders still require the app or tray process. ICS exports events only; cloud sync and ICS import remain future milestones. See [known issues](KNOWN_ISSUES.md).

## Verification

This release is covered by 77 Python tests, seven JavaScript suites, real offscreen QML editor interactions and a smoke launch. [Preparation CI passed on Python 3.10, 3.12 and 3.14](https://github.com/jonas101201/liquid-calendar/actions/runs/40734583186). A separate agent reproduced the audit findings and rechecked the corrections. The release tag identifies the final checked source commit; its checks are available on GitHub. Fresh-account installation validation remains excluded at the maintainer's request. See [TESTING.md](TESTING.md) and the [release record](docs/RELEASE_0.2.0.md).
