# Liquid Calendar 0.3.6 Beta 1

Released **28 October 2026**. English interface, Fedora/KDE Plasma, GPL-3.0-or-later.

This is the first published 0.3.x beta and includes the initial 0.3.0 milestone plus six development patches. Versions 0.3.0–0.3.5 were not published separately. See the [per-patch changelog](CHANGELOG.md).

[Release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.6-beta.1).

## Faster creation

- **Tools ▾ → Quick add** / Ctrl+Shift+N: type `tomorrow 15:00 Dentist for 45m` or `Morgen 15 Uhr Zahnarzt für 45 Minuten`. Review the interpreted title, date, time and duration before saving.
- **Date and time picking:** choose a date from a month grid with year control and Today/Tomorrow shortcuts; choose hours/minutes or a time preset. Repeat end dates also have a picker. These controls are available in the companion widget too.
- **Event templates:** use **More ▾ → Save template…** in the editor to save the current event details as a named template. Use, rename or delete templates through **Tools ▾ → Event templates**. Applying a template creates a fresh editable draft on the selected day.

- **Weekly repeat days:** select any nonempty set of weekdays in desktop and widget editors. Existing weekly records keep their original weekday. JSON and ICS exports preserve the rule, and single-occurrence edits leave future days intact.

## Event merging and overlapping entries

Open a saved event or individual occurrence and choose **More ▾ → Merge with another event…**. Select another event on the same date and review the preview before confirming. Titles, locations and notes are combined without truncation; timed entries cover the union of both ranges, including gaps. The first event keeps its identity/category, and the largest enabled reminder offset is used relative to the new start. Undo restores both entries. Concurrent edits are rejected transactionally.

Merging supports independent events and selected occurrences from repeat series, either both timed or both all-day. Open an individual occurrence before merging: only the selected occurrences become exceptions, while future repeats and other exceptions remain unchanged. The merged result is a standalone event. Tasks, whole-series edits and already detached series occurrences are excluded. Save editor changes before merging. Limit violations block the merge rather than dropping content.

The week view gives simultaneous entries separate readable lanes, expands entries into available lanes and scrolls horizontally when needed. Headings follow horizontal scrolling. Short neighboring entries use visual spacing without receiving false time-conflict badges; midnight continuations are included.

## Behavior and limits

Quick entry is a deterministic offline parser for documented syntax, not unrestricted natural language. It rejects multiple recognized dates/times. Relative dates use the current day, missing dates use the selected day, missing times use 09:00 and duration defaults to 60 minutes. Always review the preview.

Templates retain title, time, duration, category, reminder, location and notes. They exclude dates, repeats, task/completion details and series identities. Up to 50 event templates; names 1–80 characters. The library is separate from event Undo and event JSON import/export. Templates are stored in the existing local database and covered by automatic SQLite backups. Stale edits/deletions are rejected rather than overwriting changes from another app instance.

## Install and verification

The source installer and optional widget installer retain their existing workflow. Existing events need no migration. An active older widget must be reloaded via **Connect** for sharing protocol 3 before app editing is enabled. Fully quit with Ctrl+Q before reopening after an update.

122 Python tests, eight JavaScript suites, actual offscreen Qt creation/merge/menu interactions, the isolated widget editor and temporary-database smoke launches passed. The [tested source snapshot](https://github.com/jonas101201/liquid-calendar/commit/ff0988d6478d9f260b5df96a2f1b85065ab7e908) passed [hosted tests](https://github.com/jonas101201/liquid-calendar/actions/runs/40774771194) on Python 3.10, 3.12 and 3.14 and [security analysis](https://github.com/jonas101201/liquid-calendar/actions/runs/40774765474). Final release checks are recorded on the tagged commit. Fresh-account installation testing remains excluded. See [testing details](TESTING.md), [known issues](KNOWN_ISSUES.md) and [the release record](docs/RELEASE_0.3.6.md).
