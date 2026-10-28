# Liquid Calendar 0.3.0 Beta 1 — release preparation

This milestone is **not published yet**. The current public beta remains 0.2.0-beta.1. English interface, Fedora/KDE Plasma, GPL-3.0-or-later.

## Faster creation

- **Tools ▾ → Quick add** / Ctrl+Shift+N: type `tomorrow 15:00 Dentist for 45m` or `Morgen 15 Uhr Zahnarzt für 45 Minuten`. Review the interpreted title, date, time and duration before saving.
- **Date and time picking:** choose a date from a month grid with year control and Today/Tomorrow shortcuts; choose hours/minutes or a time preset. Repeat end dates also have a picker. These controls are available in the companion widget too.
- **Event templates:** use **More ▾ → Save template…** in the editor to save the current event details as a named template. Use, rename or delete templates through **Tools ▾ → Event templates**. Applying a template creates a fresh editable draft on the selected day.

- **Weekly repeat days:** select any nonempty set of weekdays in desktop and widget editors. Existing weekly records keep their original weekday. JSON and ICS exports preserve the rule, and single-occurrence edits leave future days intact.

## Behavior and limits

Quick entry is a deterministic offline parser for documented syntax, not unrestricted natural language. It rejects multiple recognized dates/times. Relative dates use the current day, missing dates use the selected day, missing times use 09:00 and duration defaults to 60 minutes. Always review the preview.

Templates retain title, time, duration, category, reminder, location and notes. They exclude dates, repeats, task/completion details and series identities. Up to 50 event templates; names 1–80 characters. The library is separate from event Undo and event JSON import/export. Templates are stored in the existing local database and covered by automatic SQLite backups. Stale edits/deletions are rejected rather than overwriting changes from another app instance.

## Install and verification

The source installer and optional widget installer retain their existing workflow. Existing events need no migration. An active older widget must be reloaded via **Connect** for sharing protocol 3 before app editing is enabled. Fully quit with Ctrl+Q before reopening after an update.

102 Python tests, eight JavaScript suites, real offscreen QML creation interactions and a temporary-database smoke launch form the preparation checks. [Hosted preparation tests](https://github.com/jonas101201/liquid-calendar/actions/runs/40749293714) passed on Python 3.10, 3.12 and 3.14. Final release CI must pass again before publication. Fresh-account installation testing remains excluded. See [testing details](TESTING.md), [known issues](KNOWN_ISSUES.md) and [the preparation checklist](docs/RELEASE_0.3.0.md).
