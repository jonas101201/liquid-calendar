# 0.3.6-beta.1 release record

Release date: **28 October 2026**.

[Release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.6-beta.1) · [Release notes](../RELEASE_NOTES.md) · [Known issues](../KNOWN_ISSUES.md)

## Included work

This is the first published 0.3.x beta, combining the original 0.3.0 baseline and six functional development patches recorded in [CHANGELOG.md](../CHANGELOG.md).

- Offline English/German quick entry, themed date/time pickers and transactional event templates.
- Styled function dropdowns and compact task filters.
- Selected weekdays for weekly repeats across calendar/search/reminders, single-occurrence changes and JSON/ICS export.
- Event merging with preview, content preservation, stale-edit rejection and Undo. Individual recurring occurrences merge without changing future repeats.
- Readable overlap lanes, short-event spacing, horizontal scrolling, aligned week headings and selected-day visibility.
- Hidden dropdown rows occupy no space; widget editor preserves task metadata and avoids a sizing loop.

## Verification

Source snapshot [ff0988d](https://github.com/jonas101201/liquid-calendar/commit/ff0988d6478d9f260b5df96a2f1b85065ab7e908) passed [hosted tests](https://github.com/jonas101201/liquid-calendar/actions/runs/40774771194) on Python 3.10/3.12/3.14 and [security analysis](https://github.com/jonas101201/liquid-calendar/actions/runs/40774765474). Coverage includes 122 Python tests, eight JavaScript suites, actual Qt creation/merge/menu interactions, isolated widget editing and smoke launches against temporary synthetic databases. Final release checks are attached to the tagged commit. Installation in a fresh user account has not been tested.

The release tag fixes the exact source used to build ZIP/TAR/SHA256SUMS. Each archive includes MANIFEST.sha256. Only source allowlisted by the builder is packaged; personal data, backups and Qt runtimes are excluded. Existing published tags/assets are not replaced.

## Compatibility

English UI; target Fedora/KDE Plasma 6. Sharing protocol 3 requires reloading an active older widget through Connect before editing. Fully quit with Ctrl+Q and reopen after updating. Local calendar records are not automatically rewritten. Merge excludes tasks, entire-series edits and already detached occurrences. Templates are covered by database backups but excluded from event JSON export and event Undo. See [KNOWN_ISSUES.md](../KNOWN_ISSUES.md) for limitations.
