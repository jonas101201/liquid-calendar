# Changelog

## 0.3.0-beta.1 — 2026-10-28

- Weekly repeats can select multiple weekdays in app and widget editors. Calendar, search, reminders, exceptions, per-occurrence changes and JSON/ICS export honor the selected days; legacy weekly records retain their original behavior.
- Sharing protocol 3 prevents editing against an active widget without weekday support until it is reloaded with Connect.
- Widget editor restores existing task priority/project/checklist fields and avoids a delete-dialog sizing loop.

- Offline quick entry with English/German dates, explicit times, am/pm, all-day input, durations and an editable preview before saving.
- Extra creation functions are grouped into Tools and editor More dropdowns, preserving the existing main layout.
- Calendar month/year grid, Today/Tomorrow shortcuts, start-time controls and repeat-end picking in app and widget editors.
- Desktop event-template library: save from the editor, use on the selected day, rename and delete without changing existing events. Templates exclude dates, repeats and series identities.
- Separate transactional template storage with a 50-template limit, Unicode-aware validation and stale-edit conflict protection. Automatic SQLite backups include templates; event JSON export does not.
- Regression checks cover parsing ambiguity, preview-only behavior, template persistence/concurrency and actual QML creation flows.

## 0.2.0-beta.1 — 2026-10-28

- No/low/medium/high task priorities with filtering and sorting.
- Editable checklists, inline completion and progress counters; per-occurrence progress for repeating tasks. Typed step titles and editor checkboxes update the saved draft correctly, including after adding another step.
- Projects with task counts, filtering, sorting, renaming, merging and clearing assignments without deleting tasks.
- Global search includes project names and checklist steps across all dates.
- JSON backup/import and companion-widget editing preserve the new optional task details. Existing records need no migration.
- Project Undo restores the previous project filter, while preserving a different filter subsequently chosen by the user.
- Project summaries aggregate records in one pass rather than scanning all tasks for each project.
- Unicode limits agree between Python, the app editor and the widget; valid emoji text survives editing and duplication without truncation.
- Expanded inline checklists stay open after completion, including when a recurring occurrence is detached.
- Project rename/merge/clear rejects a concurrent change in project membership instead of silently leaving some assignments behind.
- Added regression tests for validation, concurrent edits, recurrence, backups, scheduling, project operations, Unicode boundaries and real QML keyboard/editor behavior.

## 0.1.1-beta.1 — 2026-10-28

- Completing a repeating task now completes only the selected occurrence. Reopening that completed occurrence preserves future repetitions. Legacy whole-series completions can still be explicitly reopened.
- Calendar fallback Undo now restores detached occurrences with the parent series. The native app already hides the fallback action and uses its complete app-wide Undo.
- All-day reminders sent one day early identify the event as tomorrow.
- Agenda conflict detection uses daily interval groups instead of comparing every occurrence pair across the entire range.
- SQLite transactions close their connections immediately, including rollback/error paths.
- Added regression coverage for group restore, repeating-task completion, concurrent toggles, reminders, randomized overlaps and connection lifetime.

## 0.1.0-beta.1 — 2026-10-28

First public beta. Earlier 1.x version numbers were internal development labels.

- English interface, notifications, validation and English date search.
- Today, week, month and 7/14/30-day agenda views.
- Undated tasks, categories, status/planning filters and sorting.
- Daily/weekly/monthly/yearly repeats with individual-occurrence edits.
- Time-slot suggestions with availability checks and drag-to-reschedule.
- Reminders, optional login startup, themes and reduced motion.
- Local shared SQLite storage, conflict detection, daily backups and undo.
- JSON backup/import and event-only ICS export.
- Optional companion widget for Plasma 6.

Fresh-account installation validation was explicitly omitted for this beta. See KNOWN_ISSUES.md and TESTING.md.
