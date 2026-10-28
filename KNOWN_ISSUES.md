# Known issues and beta limitations

Applies to **Liquid Calendar 0.2.0-beta.1**. Last updated: **2026-10-28**.

This page distinguishes current limitations from issues fixed in earlier beta versions. It is not a guarantee that the beta is free of bugs.

## Current limitations

- **Platform support:** the target is Fedora Linux with KDE Plasma 6. Windows, macOS and other Linux desktops are not validated. Successful offscreen CI checks do not establish full desktop compatibility.
- **Installation:** Python 3.10–3.14, venv/pip support and network access to PyPI are required. The installer is not an offline installer; Qt platform libraries must be supplied by the operating system.
- **Language:** the interface is English only. There is no language selector or complete localization framework yet. German date-query aliases remain available as input compatibility.
- **Synchronization:** data is stored locally. Account sync, mobile apps and collaborative calendars are not implemented.
- **Reminders:** the app must remain open or run in the system tray. Notifications use `notify-send`. Closing the window may keep reminders running; **Ctrl+Q** fully quits.
- **Planning:** time suggestions cover 09:00–18:00. Times are local floating times; timezone-aware invitations and travel-time planning are not supported.
- **Import and export:** JSON import adds new IDs and preserves existing IDs. ICS export includes events, not tasks. ICS import is not implemented.
- **Shared storage:** app and widget use the same local Plasma database. If an incompatible active widget is detected, editing is blocked until **Connect** reloads it. This briefly refreshes the desktop and panels.
- **Undo:** app-wide Undo covers the last local app change and refuses to overwrite a newer edit of the same entry. It is not an unlimited history or backup restoration tool.

## Task organization scope in 0.2.0

- Projects are task labels, created when assigned to a task. Empty projects are not retained. Names are case-sensitive; renaming to an existing name merges assignments. Clearing a project does not delete its tasks.
- Project counters count stored task records, including detached occurrences, rather than an infinite recurring schedule.
- Checklist completion is independent of the task's completion. Inline checklist changes affect only the selected occurrence; editing **Series** changes the series template.
- Up to 100 steps per checklist, 200 characters per step and 80 characters per project name. Limits count Unicode code points consistently across app and widget. The project name `*` is reserved for the all-projects filter.
- The companion widget supports editing task details; the full project overview and combined organization filters are in the desktop app.

## Updating from 0.1.x

- Task details are optional; old records are not rewritten. JSON backups preserve priority, project and checklist fields. Future older-version compatibility is not guaranteed; retain a backup before downgrading.


- Fully quit the running app with **Ctrl+Q** and reopen it after updating. Reload an active desktop widget to activate its corrected task-completion behavior.
- Existing stored completion states are not automatically rewritten. If an older version marked a whole recurring task series completed, explicitly reopen that series to make its future occurrences available again.
- The update does not introduce a new database format or automatically reconstruct previously missing records. Keep backups of important calendar data; see the [README](README.md#data-and-privacy).

## Fixed in 0.1.1-beta.1

The following audited issues are fixed and should not be treated as current limitations:

- Completing a recurring task now affects the selected occurrence rather than all future repetitions. Reopening a completed occurrence does not create duplicates; stale concurrent completion attempts are rejected.
- Calendar fallback Undo restores detached occurrences together with the parent series. **Audit clarification:** this internal fallback was already hidden in the native app; the visible app-wide Undo already supported complete group restoration.
- A next-day all-day reminder identifies the event as tomorrow instead of saying “All day today”.
- Agenda conflict calculation uses daily overlap groups rather than comparing every occurrence pair across the entire date range.
- SQLite connections close immediately after transactions, including error and rollback paths.

See the [changelog](CHANGELOG.md), [testing details](TESTING.md) and [roadmap](ROADMAP.md) for release history, validation scope and planned features.

## Reporting a new issue

Use [GitHub Issues](https://github.com/jonas101201/liquid-calendar/issues) and include your app version, OS/Plasma/Python versions, reproduction steps, and expected versus actual behavior. Use synthetic examples or redact private information; do not upload personal calendar databases.
