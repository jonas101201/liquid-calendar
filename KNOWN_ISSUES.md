# Known issues and beta limitations

Applies to **Liquid Calendar 0.3.9.2 Beta 2** (`0.3.9.2-beta.2`). Last updated: **2026-10-30**.

This page distinguishes current limitations from issues fixed in earlier beta versions. It is not a guarantee that the beta is free of bugs.

## Confirmed open bugs

The Flatpak beta uses asynchronous Notification portal calls and is not affected by the two native `notify-send` issues below. Its interactive file-picker and login/autostart acceptance checks remain separate from the isolated tests; see [Flatpak limitations](flatpak/README.md).

These native notification issues remain present in 0.3.9.2 Beta 2; the Flatpak uses a different portal backend. Confirmed with isolated synthetic records on **2026-10-30**; an independent review reproduced both.

### Native reminder titles beginning with a hyphen can suppress delivery

- **Reproduce:** create an event titled `--help` with an enabled reminder and keep the app running until it is due.
- **Actual behavior:** the title is passed to `notify-send` without an end-of-options separator. `notify-send` interprets `--help` as an option, exits successfully without displaying the reminder, and the app records it as delivered. Other option-like titles can also be misinterpreted.
- **Expected:** every event title is treated as notification text.
- **Workaround:** start reminder titles with a letter or number rather than `-`.
- **Status:** open; notification argument handling needs correction and a regression test.

### Native slow notification delivery blocks the interface

- **Reproduce:** a due reminder runs while `notify-send` or its notification service responds slowly. An isolated event-loop check with a simulated 350 ms notification call delayed a 20 ms Qt timer until approximately 352 ms.
- **Actual behavior:** reminder delivery uses a blocking subprocess on the GUI thread. The interface cannot process input during that call. The timeout is up to eight seconds per due reminder; several due reminders can accumulate delays.
- **Expected:** notification delivery does not block interaction with the calendar.
- **Workaround:** pause reminders if notification delivery repeatedly stalls. This disables notifications until reminders are enabled again.
- **Status:** open; delivery needs asynchronous processing with correct success/failure tracking.

## Fixed in 0.3.9.2 Beta 2; still present in 0.3.9.1

The following bugs affect the published **v0.3.9.1** snapshot. Corrections are included in **0.3.9.2 Beta 2**; the existing **0.3.9.1 release archives do not include them**. See the [follow-up audit](docs/BUG_AUDIT_0.3.9.1_FOLLOWUP.md).

| Issue | Reproduction and impact | Workaround in the published version |
| --- | --- | --- |
| Existing export can be damaged by a failed write | Export over an existing JSON/ICS file; an interrupted or partial write can replace it with incomplete content. Development exports use an atomic commit. | Export to a new filename and retain the previous backup. |
| Export can miss a recent widget edit | Save a change in the widget and immediately export from the app before its next refresh (about 2.5 seconds). The export can contain the cached, older records. | Wait for the change to appear in the app before exporting. |
| Undated task save changes Calendar mode | Save an undated task in the desktop app, then open Calendar. An internal task filter can replace the month grid with task results. | Reset the embedded calendar's task filter to All. |
| Today/date navigation stays hidden behind search | Search in Calendar, then use Today or Jump to date. The selected date changes while the old search still hides the grid; period arrows can also change an invisible selection. | Clear the Calendar search and reset its task filter before navigating. |
| Failed preference writes leave a temporary active value | A disk/permission error while saving theme, motion or reminders can change the running setting without saving it. After reopening, the previous setting returns. | Resolve the storage error, reopen the app and apply the setting again. |
| Unsupported early-year date input | Enter a DMY date such as `1.1.0001`. Date hints can accept a year below the supported range, leading to inconsistent resolution or search errors. | Use dates within years 1000–9999. |
| Widget ICS end times and text can be incorrect | Export an event spanning a daylight-saving transition using the widget. End time can differ from the app's floating wall time; long Unicode lines are not folded correctly and carriage returns are handled inconsistently. | Prefer desktop-app ICS export for these events; retain a JSON backup. |
| ICS export fails at the upper date boundary | An event whose end falls beyond year 9999 cannot be represented. Desktop errors are technical; widget output can contain an unsupported year, and widget export errors are not handled consistently. | Adjust the event so its end stays within year 9999, or use JSON backup. |

## Fixed in 0.3.9.1

The Calendar Month/Week control now supports held-pointer dragging. Month-card Open edits the selected repeating occurrence rather than the whole series, while Series keeps whole-series editing available. Overnight continuations are visible on the following day and retain the source occurrence date for edits and completion. See the [follow-up audit](docs/BUG_AUDIT_0.3.9_FOLLOWUP.md).

## Fixed in 0.3.9

The interface update corrects duplicate native shortcuts, inaccessible appearance settings, inconsistent picker/menu colors, disappearing week hour labels, a misplaced Settings scrollbar and interrupted popup flashes. Opacity changes no longer write settings and rebuild calendar models for every pointer movement. Draft-aware merging keeps unsaved editor values and rejects concurrent duplicate operations. See [the UI audit](docs/UI_AUDIT_2026-10-29.md).

## Fixed in 0.3.7-beta.1

The public 0.3.6 beta can return an unrelated date for an exact search matching a cancelled series start, suggest a quarter-hour that has already begun, accept a competing booking inserted between availability check and save, and overflow when rendering or searching some dates at the maximum supported year. The 0.3.7 release corrects these; see the [audit record](docs/BUG_AUDIT_0.3.7.md).

## Current limitations

- **Platform support:** the target is Fedora Linux with KDE Plasma 6. Windows, macOS and other Linux desktops are not validated. Successful offscreen CI checks do not establish full desktop compatibility.
- **Native installation:** Python 3.10–3.14, venv/pip support and network access to PyPI are required. The installer is not an offline installer; Qt platform libraries must be supplied by the operating system.
- **Language:** the interface is English only. There is no language selector or complete localization framework yet. German date-query aliases remain available as input compatibility.
- **Synchronization:** data is stored locally. Account sync, mobile apps and collaborative calendars are not implemented.
- **Reminders:** the app must remain open or run in the system tray. Notifications use `notify-send`. Closing the window may keep reminders running; **Ctrl+Q** fully quits.
- **Planning:** time suggestions cover 09:00–18:00. Times are local floating times; timezone-aware invitations and travel-time planning are not supported.
- **Import and export:** JSON import adds new IDs and preserves existing IDs. ICS export includes events, not tasks. ICS import is not implemented.
- **Shared storage:** the native app and widget use the same local Plasma database. Flatpak uses isolated data by default and requires explicit permissions for optional shared-widget mode. If an incompatible active widget is detected, editing is blocked until **Connect** reloads it. This briefly refreshes the desktop and panels.
- **Undo:** app-wide Undo covers the last local app change and refuses to overwrite a newer edit of the same entry. It is not an unlimited history or backup restoration tool.

## Reworked event linking in 0.3.9.2 Beta 2

The earlier display incorrectly treated related contained events as competing overlaps, and inner cards could cover the outer title. Both problems are corrected in this source update.

Version 0.3.9.2 replaces the previously incorrect destructive merging and conflicting linked-card display with **More → Link with another event…**. Two separate cards retain individual titles, times, details, categories and reminders. Shared labels identify the relationship. In the week view, a fully contained timed member is inset into its longer background event, with both occupying one outer lane. Linked members do not produce mutual conflict warnings; unrelated bookings still do. Equal, very short or partially overlapping intervals retain separate cards. Both can be edited, moved or deleted individually; **Unlink group** removes the relationship while retaining both entries and current editor changes. One Undo reverses the most recent operation.

Creating a link currently requires two unlinked events on the same date with matching all-day mode. Individual recurring occurrences can be linked without changing future repeats; tasks and whole series are excluded. Existing groups must be unlinked before choosing a different partner. Moving an event to another date preserves the relationship; badges identify links across dates, while containment is calculated from the visible segments on each day. A containing segment needs at least 90 minutes of display space; if a filter hides its parent, the child renders as a normal card. Deleting a member or converting it into a task/series clears a leftover singleton link.

JSON backups preserve links. ICS exports the events separately without the app-specific grouping relationship. Older destructive merges cannot be automatically separated because the original independent fields were not retained. Existing records are not reconstructed or migrated.

See [event linking](docs/EVENT_LINKS.md) for the workflow. This behavior is included in 0.3.9.2 Beta 2; existing 0.3.9.1 downloads remain unchanged.

## Event merge scope in the published 0.3.9.1

Desktop **More → Merge with another event…** includes current editor changes and combines events or selected occurrences matching the edited date and all-day mode. Only selected source occurrences are cancelled; future repeats remain unchanged and the result is standalone. Tasks, whole-series edits and already detached occurrences are excluded. Invalid drafts and concurrent source changes block the operation without partial writes. Cancel preserves the editor draft and writes nothing. One Undo restores both original saved sources.

A combined event has the first event's edited category and one reminder (the largest enabled offset relative to the combined start). The combined time range includes gaps between the originals. Length/duration limits block the operation without truncation.

## Weekly repeat compatibility

Selected weekdays are supported for weekly repeats; monthly/yearly positional weekday rules are not implemented. Old weekly records keep their original weekday if no selection is stored. An active older widget must be reloaded using Connect before editing with sharing protocol 3. Downgrading to a client without weekday support can misinterpret the schedule; retain backups. No existing events are automatically rewritten.

## Creation scope in 0.3.0

- Quick entry recognizes documented date/time/duration syntax. It does not infer recurring schedules, locations, timezones or arbitrary natural language. Date-like words in a title can be interpreted as scheduling input; review the preview and edit the title if needed.
- Event templates exclude dates and repeat/series identities. Task templates are not implemented. Template creation and library management are desktop-app functions; the widget includes date/time pickers.
- Templates live in a separate SQLite state key. Automatic database backups include them; event JSON export/import does not. Template rename/delete is not part of event Undo.
- Pickers use local dates and 24-hour times. Manual date/time fields remain available. Live Plasma widget validation on multiple desktop configurations remains outside offscreen checks.

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
