# 0.3.7 bug audit — 28 October 2026

Scope: targeted review after 0.3.6-beta.1, isolated synthetic records only. No fresh-account installation tests, personal database inspection or automatic data migration. This record is not a guarantee that all bugs have been found.

## Findings and corrections

1. Exact date searches could match the stored series start after that occurrence was cancelled, showing a different representative day. ISO/DMY and exact relative-day queries now require an occurrence on the requested day, consistently in Python and both JavaScript clients. Undated tasks remain searchable by ordinary text.
2. Planning at 09:00:59 still offered 09:00. The quarter-hour floor now accounts for seconds/microseconds, in both suggestions and final validation.
3. The independent reviewer reproduced a booking race by inserting a competing event between the preliminary check and task save. Store.merge now checks the latest calendar inside BEGIN IMMEDIATE before applying a planned task move. The injected race is rejected without changing the task; moving its own occurrence still succeeds.
4. The reviewer reproduced an overflow when a weekly recurrence had no next date within year 9999. Python scans and JavaScript candidates are bounded, and Python instances exclude overflowing carry segments.
5. The reviewer reproduced overflow in the final week's headers. Nonexistent cells render as unavailable, drop targets are disabled, navigation stays in years 1000–9999 and out-of-range calendar selection is ignored.

## Review sequence

Findings 1–2 were reproduced and corrected, then independently verified. The review identified findings 3–5, which were corrected and checked again. A temporary Drag.keys regression was found during the week-cell change and corrected before verification. The final independent check found no remaining actionable defect in the reviewed corrections. This is a scoped result, not a guarantee of universal bug freedom.

## Verification

- 131 Python tests passed, including an injected second-client booking and supported date-boundary regressions.
- All eight JavaScript suites passed for app/widget calculations and exact-date behavior.
- Actual Qt interactions and rendering passed, including endpoint week views, event merging, templates, pickers and menu rows; no QML errors were recorded.
- The isolated widget editor check passed; it stubs only Kirigami theme lookup and uses a temporary database.
- Temporary-database smoke launches passed.
- The independent second reviewer confirmed the transaction race fix, unchanged future data, safe date endpoints, exact search and time rounding; it found no remaining actionable issue in the reviewed fixes.

The audit preceded publication of 0.3.7-beta.1. The installed version is 0.3.7-beta.1; application/widget files are backed up before replacement. Personal calendar records are not opened or rewritten by the updater. Reload the app and, when convenient, the active widget to load new code.
