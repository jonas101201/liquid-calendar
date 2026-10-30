# Functional audit after 0.3.9.1 — 29 October 2026

Scope: development corrections following the published 0.3.9.1 snapshot. Calendar records are not migrated.

## Confirmed findings and corrections

- **Month state leakage:** saving a native undated task applied the standalone calendar's global task filter. Returning to Calendar then displayed tasks instead of its month grid. Native saves now route to Tasks; standalone behavior remains appropriate to the widget.
- **Hidden date navigation:** Today and the date dialog could change the selected date while an old month search still hid the grid. These controls now clear month search/task mode. Period arrows stay disabled while displaying global results.
- **Stale exports:** JSON/ICS exports used the app's cached records and could miss another client's most recent committed edit before polling. Exports now read one fresh database snapshot.
- **Partial backup replacement:** writing directly to an existing export could truncate it on an I/O error. QSaveFile now commits only a complete write. Partial-write/read-failure regressions preserve the previous export.
- **Failed preference writes:** theme, reminders and motion changed in memory before persistence succeeded. They now adopt changes only after a successful write; theme choice bindings are restored on failure.
- **Unsupported date hints:** DMY hints accepted years below the supported 1000–9999 range and could cause inconsistent resolution/search. All hints respect the supported bounds.
- **ICS consistency:** JavaScript export previously used elapsed milliseconds across daylight-saving changes while the calendar uses floating wall time. Calendar-based end calculations now agree with Python. Exports reject unsupported start/end ranges with a useful error, fold long UTF-8 lines without splitting code points, and normalize carriage returns consistently.
- **ICS error presentation:** JavaScript export buttons now calculate the complete result before updating transfer state. Errors are shown without losing existing import text or exposing partial output.

## Additional open findings — 30 October 2026

An independent follow-up reproduced two reminder defects that remain unfixed in this development snapshot:

- An event title of `--help` is interpreted by `notify-send` as an option. The command exits successfully without displaying a notification, so the app incorrectly records delivery. The reproduction used the real command and an isolated synthetic database.
- Reminder subprocesses run synchronously on the GUI thread. With a simulated 350 ms notification command, a 20 ms Qt callback ran at approximately 352 ms. The configured timeout permits up to eight seconds of blocked interaction per due notification.

Reproduction, impact, status and temporary workarounds are recorded in [Known issues](../KNOWN_ISSUES.md). These are distinct from the development corrections above.

## Verification

156 Python tests, all eight JavaScript suites, actual native QML interactions, isolated widget editing, source-copy synchronization and temporary-database smoke launch form the final validation set. Tests use synthetic records and isolated databases.

An independent agent reproduced the date/ICS problems and a partial-write failure, implemented the date/ICS corrections, and independently reviewed the native navigation, preference and fresh-export fixes. A second verification round checks the atomic export path and both JavaScript error handlers. Tests cover daylight-saving transitions in Europe/Berlin, long emoji/Japanese strings, date bounds, real theme-card clicks and preservation of existing output/import text.

This is a bounded audit, not a guarantee that every supported desktop interaction is bug-free. Live Plasma behavior and installation in a fresh user account are not established by the isolated checks.
