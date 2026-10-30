# Changelog

**0.3.6-beta.1** is the cumulative public release of the 0.3.x development work. Versions 0.3.0–0.3.5 below are unpublished historical snapshots. Patch numbers were assigned retrospectively on 28 October 2026, one per functional code patch after the initial 0.3.0 baseline. Source links identify the original implementation commits, which retain their original version strings. No commits or published tags were rewritten. Documentation-only commits are not numbered separately.

## 0.3.9.3 — 2026-10-31

Beta prerelease.

- Keep popup closing scale monotonic when closing during the first opening frames; closing no longer grows an early, partially opened popup.

- Publish only validated, complete automatic SQLite backups. Repair incomplete daily files left by previous failures, preserve valid snapshots, serialize concurrent creators and retry after copy/publish errors.
- Preserve nested-event start times during horizontal date dragging; apply 15-minute deltas only for vertical movement, including non-quarter-hour starts.
- Close remote Flatpak autostart requests on timeout, follow alternative returned handles and allow subsequent requests without orphaned dialogs.
- Add interrupted-copy, repair, atomic-publish and concurrent-client regressions, real nested-card mouse drags, and private D-Bus cancellation/retry checks.

## 0.3.9.2-beta.2 — 2026-10-30

Beta prerelease. Publishes the corrected event-linking source below and the first separate Flatpak package. The previous merge/display implementation was incorrect for contained related events and could obscure outer titles; both behavior and card design have been reworked.

- Add a separate local Flatpak beta with KDE/PySide runtime sharing, sandbox-local storage, asynchronous notification and autostart portals, desktop metadata and a reproducible local bundle builder.
- Keep native data intact; document JSON import and optional shared-widget permissions. Prune unused BaseApp generators, WebEngine and development dependencies. Destroy QML before its bridge on shutdown to prevent teardown binding errors.

## 0.3.9.2 — 2026-10-30

Beta source update.

**Reworked event merging:** the previous implementation was incorrect for related events such as School 07:00–14:00 and Exam 09:00–10:00. It combined independent event content or displayed intentionally related events as conflicting side-by-side bookings. Early inner cards could also cover the containing event's title. This update keeps independent records, renders contained events inside the longer background card, suppresses only mutual group conflicts, protects the header and simplifies the card design. Unrelated conflicts remain visible. Previously destructively merged records cannot be reconstructed automatically.

- Simplify week cards with title-first typography, muted time ranges, balanced inner spacing and subtle category accents. Remove repeated link icons and nested group labels; keep complete relationship details in tooltips. Inset cards retain their actual end position when a header clearance is needed.

- Reserve a clear two-line header for containing week cards so early inner events cannot cover their title. Short containing intervals fall back to separate readable cards without mutual conflict warnings.

- Nest contained linked events in their longer background event using one outer week lane. Suppress mutual group conflict warnings while preserving unrelated conflicts, individual editing and dragging, time ranges, and filter/overnight handling.

- Replace destructive event merging with linked, separate event cards. Preserve each title, time, category, notes and reminder; show paired previews, link badges and week-view connection lines.
- Add Unlink group with draft preservation and Undo. Editing or moving one member leaves the other intact; deleting or converting a member removes the surviving stale link. JSON preserves groups, while ICS exports individual events.

- Keep native undated-task saves in Tasks without changing the embedded month filter. Today and date jumps leave month search mode; period navigation is disabled during global results.
- Export fresh shared data and atomically replace completed JSON/ICS files, preserving an existing backup if reading or writing fails.
- Keep active theme, reminder and motion settings unchanged when their persistence fails; restore the visible theme choice after an error.
- Reject unsupported date hints and report unrepresentable ICS date ranges clearly. Align widget ICS floating-time calculations across daylight-saving transitions, Unicode line folding and carriage-return handling with the app.
- Present JavaScript ICS errors without destroying existing import text or showing a partial export.

## 0.3.9.1 — 2026-10-29

Beta prerelease.

- Show overnight events on the following day in month/widget calendars, mark them as Continued and retain the source occurrence date for editing and task completion.

- Open the selected repeating occurrence from the month view, consistently with Today and Week. A separate Series action retains access to whole-series editing.

- Make the Calendar Month/Week selection draggable with the mouse held down. The glass indicator follows the pointer and snaps to the chosen view on release, while clicks and keyboard activation remain available.

## 0.3.9 — 2026-10-29

Beta prerelease.

- Derive the complete light/dark interface palette from the selected accent: backdrop, glass panels, input fields, menus, timeline axis, hover states and theme previews. Category and conflict colors keep their semantic roles.

- Keep opacity dragging local to the glass preview, persist once on release and debounce keyboard adjustments. Appearance changes emit a dedicated visual signal instead of rebuilding calendar data, and repeated identical settings are not rewritten.

- Add distinct live previews for Dark glass, Light glass and System appearance. System mode follows the desktop palette brightness. Apply the selected theme/accent to all filter and project menus, including checked sort options.

- Include unsaved editor changes in merge previews and the atomic final merge. Use the edited date/all-day mode for candidates, preserve series identity and conflict checks, and restore both original saved events with one Undo.

- Give native calendar shortcuts a single owner and block background actions while dialogs are open.
- Restore app-wide accent and glass-opacity controls in Settings, persist their values, and align picker/menu colors with the chosen accent.
- Keep the week time axis visible while scrolling; anchor the Settings scrollbar at the right edge.
- Close interrupted popup entrances from their current frame to prevent a flash.

- Replace neutral gray desktop surfaces with clearer ocean-blue glass and ice/cyan accents. Calendar scrollbars respond immediately to track presses and thumb dragging, with larger hit areas and keyboard navigation.

- Add sliding navigation and calendar selection, gentle section entrances, glass hover reflections and softly expanding desktop dialogs. Reduced motion disables these transitions.

- Consolidate month and week under Calendar, remembering the selected presentation when returning from another section.
- Remove the duplicate desktop calendar header and provide one shared period toolbar.
- Add translucent surfaces, softly lit glass edges and a flowing backdrop in both light and dark themes, respecting reduced-motion preferences.

## 0.3.8.1 — 2026-10-28

Beta prerelease. The 0.3.8-beta.1 preparation was not published separately.

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
- Regression tests cover injected concurrent bookings, exact-date results, sub-minute timing and actual Qt rendering at date endpoints. The fixes underwent an independent review and a second verification round; see the [audit record](docs/BUG_AUDIT_0.3.7.md).

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

Installation in a fresh user account has not been validated for this beta. See KNOWN_ISSUES.md and TESTING.md.
