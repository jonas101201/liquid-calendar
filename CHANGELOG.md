# Changelog

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
