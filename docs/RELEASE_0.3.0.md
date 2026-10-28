# 0.3.0-beta.1 release record

Release date: **28 October 2026**, published at the maintainer's request.

[Release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.0-beta.1) · [Release notes](../RELEASE_NOTES.md) · [Known issues](../KNOWN_ISSUES.md)

## Included features

- Weekly repeats with a nonempty selection of weekdays, matching calendar/search/reminder behavior and JSON/ICS BYDAY export. Legacy defaults and per-occurrence changes are preserved.
- The main layout is retained, with additional functions under Tools and editor More dropdowns. Task filters are grouped in a compact adaptive toolbar.
- Quick entry with documented English/German dates, times, durations and an editable preview before saving.
- Date/month/year and start-time pickers, including repeat-end dates, in desktop and widget editors.
- Desktop event-template save/use/rename/delete, with date-independent defaults and fresh event IDs. Template state has validation, caps and transactional stale-edit protection.
- Widget editor restores existing priority/project/checklist data; its dialog sizing loop is corrected.

## Verification evidence

The final feature snapshot [`cee2068`](https://github.com/jonas101201/liquid-calendar/commit/cee206891d22d9520aeffe7538c977dd8dc506aa) passed [hosted tests](https://github.com/jonas101201/liquid-calendar/actions/runs/40753058768) on Python 3.10, 3.12 and 3.14 and [security analysis](https://github.com/jonas101201/liquid-calendar/actions/runs/40753054074).

Coverage includes 102 Python tests, eight JavaScript suites, actual Qt dropdown/keyboard, preview/editor, date/time/typed-year, template CRUD and weekday-button flows. The isolated widget editor uses a temporary offline database and stubs only the Kirigami theme lookup. The [release PR](https://github.com/jonas101201/liquid-calendar/pull/2) records the source history and later publication checks.

The release tag identifies the exact checked commit used to build the source ZIP and TAR. Uploaded assets and digests are visible on GitHub; SHA256SUMS covers the custom source archives and each archive contains MANIFEST.sha256. Existing published tags and assets are not overwritten.

## Compatibility and limits

Existing calendar records are not automatically rewritten. Selected-weekday schedules require sharing protocol 3; reload an active older widget through Connect before editing. Older clients may misinterpret such schedules, so retain backups before downgrading.

Quick entry is a limited parser, not arbitrary natural language. Templates exclude dates/repeats/series identity and are separate from event Undo and event JSON export; automatic SQLite backups include them. Task templates are not implemented.

All test databases and screenshots use synthetic data. The local development app/widget were updated with program-file backups and an installed-app smoke launch without opening personal calendar data. Offscreen checks do not establish live Plasma compatibility on every system; fresh-account installation testing remains excluded. Existing reminder, synchronization and platform limitations remain applicable.
