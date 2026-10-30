# Liquid Calendar 0.3.9.2

Beta source update · **30 October 2026**.

## Reworked event merging and display

The previous implementation was incorrect for intentionally related events. It combined separate contents or displayed related events as conflicting, side-by-side bookings. A contained card could also cover its outer event's title. These behaviors have been reworked.

- **Separate records:** each event retains its title, time, duration, details, category and reminder. Use **More → Link with another event…** to preview and save a relationship.
- **Nested display:** School 07:00–14:00 can contain an independent Exam 09:00–10:00 card in one outer lane. Mutual group overlap warnings are suppressed; unrelated conflicts remain visible.
- **Individual editing:** open, move or delete either event independently. Unlink group preserves both events and saves valid editor changes. Undo restores the previous saved state.
- **Cleaner cards:** title-first typography, muted time ranges, subtle accents and balanced spacing replace repeated icons and group labels. The outer header stays clear.
- **Recurring occurrences:** only selected occurrences are detached; future repetitions retain their schedules.

## Additional corrections

Undated task saves no longer contaminate the month filter; Today/date jumps clear hidden month searches. Exports read fresh shared records and atomically replace files. Failed preference writes preserve the active saved values. Date-boundary checks, ICS daylight-saving calculations, Unicode line folding and export-error presentation are corrected.

## Validation and limits

172 Python tests, eight JavaScript suites, actual native QML interactions, a dedicated nested-card geometry/edit-target check in Dark and Light, isolated widget editing, shared-source synchronization and smoke launch form the validation set. Synthetic databases are used throughout. See [testing](TESTING.md).

Short, equal or partially overlapping linked intervals remain separate cards; containing segments need at least 90 minutes of display space. JSON preserves links; ICS exports independent events without app-specific grouping. Previously destructively combined records cannot be automatically reconstructed. Reminder delivery defects remain open; see [Known issues](KNOWN_ISSUES.md).

This repository update sets the source version to **0.3.9.2**. The latest packaged download remains [0.3.9.1](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.9.1); its existing archives are unchanged. Fully quit with **Ctrl+Q** before reopening an updated installation.
