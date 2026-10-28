# Changelog

**0.3.6-beta.1** is the cumulative public release of the 0.3.x development work. Versions 0.3.0–0.3.5 below are unpublished historical snapshots. Patch numbers were assigned retrospectively on 28 October 2026, one per functional code patch after the initial 0.3.0 baseline. Source links identify the original implementation commits, which retain their original version strings. No commits or published tags were rewritten. Documentation-only commits are not numbered separately.

## 0.3.8.1 — 2026-10-28

Beta prerelease, using the maintainer-requested version. The 0.3.8-beta.1 preparation was not published separately.

- Share identical text-field, checkbox and editable-number controls between editors and date/time pickers, preserving their palette bindings and interaction behavior.
- Treat qml/ as the canonical source for shared controls/calendar JavaScript. Synchronize standalone widget copies with scripts/sync_widget_sources.py and reject drift in CI, source packaging and installation before changing installed files.
- Reuse the existing occurrence_draft helper for task completion, checklist edits and moves; retain stored identities, exceptions and transactional conflict checks.
- Replace wildcard logic imports with explicit dependencies and expand Bridge initialization for readability.
- Validate with existing regression suites, distribution checks and before/after synthetic renders. No schema migration, new feature or visual redesign.

## 0.3.7-beta.1 — 2026-10-28

- Exact ISO/DMY date and relative-day searches return actual occurrences only, excluding cancelled days and undated title matches. App and widget agree.
- Planning suggestions and final validation advance past already-started minutes, including seconds/microseconds.
- Revalidate task scheduling availability inside the SQLite write transaction, rejecting bookings inserted after the initial check.
- Bound recurrence scans and week rendering/navigation to the supported date range; disable drop targets for nonexistent days.
- Regression tests cover injected concurrent bookings, exact-date results, sub-minute timing and actual Qt rendering at date endpoints. An independent agent reviewed the fixes and performed a second verification round; see the [audit record](docs/BUG_AUDIT_0.3.7.md).

## 0.3.6-beta.1 — 2026-10-28

Source: [`144d3e5`](https://github.com/jonas101201/liquid-calendar/commit/144d3e518c02163168491443a376711228a1908f).

- Merge individual recurring occurrences without changing future repeats. The merged result is standalone; Undo restores both original occurrences.
- Reject stale or forged occurrence drafts and concurrent series edits transactionally.
- Remove empty rows left by hidden dropdown actions in app and widget controls.

## 0.3.5-beta.1 — Unreleased

Source: [`279ff9a`](https://github.com/jonas101201/liquid-calendar/commit/279ff9ac055708747710d1006e61f31608c19ffa).

- Automatically bring the selected day into view when overlap lanes widen the week.
- Keep the horizontal scrollbar visible when more days are available offscreen.

## 0.3.4-beta.1 — Unreleased

Source: [`f702a8d`](https://github.com/jonas101201/liquid-calendar/commit/f702a8d1c290bdf5909dd01cee7a5b823d71aae1).

- Add desktop event merge with preview, combined content, transactional stale-edit rejection and Undo.
- Fix dense overlap cards exceeding their lanes and short cards obscuring adjacent entries; expand into available lanes, add readable horizontal scrolling and synchronize week headings.
- Stop release publication and restore preparation metadata at the maintainer's request.

## 0.3.3-beta.1 — Unreleased

Source: [`cee2068`](https://github.com/jonas101201/liquid-calendar/commit/cee206891d22d9520aeffe7538c977dd8dc506aa).

- Select multiple weekdays for weekly repeats in app and widget editors. Calendar, search, reminders, exceptions, single-occurrence changes and JSON/ICS export honor the selected days; legacy weekly records retain their original behavior.
- Sharing protocol 3 blocks editing against an active older widget until Connect reloads it.
- Restore existing task priority/project/checklist fields in the widget editor and fix its delete-dialog sizing loop.

## 0.3.2-beta.1 — Unreleased

Source: [`2acfb8c`](https://github.com/jonas101201/liquid-calendar/commit/2acfb8c95793db2fe73f7c44e59ceb177d2bf3fa).

- Group task filters into a compact adaptive toolbar, including schedule dropdown, sort/count placement and reset controls.

## 0.3.1-beta.1 — Unreleased

Source: [`76069ce`](https://github.com/jonas101201/liquid-calendar/commit/76069ce3f021917476dad3d2a348e2c672c8656a).

- Preserve the core layout and group creation functions in styled Tools and editor More dropdowns.

## 0.3.0-beta.1 — Unreleased baseline

Source: [`5492bc9`](https://github.com/jonas101201/liquid-calendar/commit/5492bc9494d806be7edda4056d7786aa1fc472d2).

- Offline quick entry with English/German dates, explicit times, am/pm, all-day input, durations and an editable preview before saving.
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
