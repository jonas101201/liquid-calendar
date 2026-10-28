# Liquid Calendar 0.1.1 Beta 1

[Published release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.1.1-beta.1) · [Full changelog](CHANGELOG.md)

Bug-fix prerelease for the first public beta. English interface, Fedora/KDE Plasma, GPL-3.0-or-later.

## Fixed

- Completing a repeating task affects only the selected occurrence; future tasks remain open. Completed one-off occurrences can be reopened. Previously completed whole-series records can be explicitly reopened as a series.
- Calendar fallback Undo restores the complete group, including detached occurrences. The native app already hides that internal fallback; its visible app-wide Undo remains the supported action.
- Next-day all-day reminder text now says “All day tomorrow”.
- Faster agenda calculation through daily overlap groups and heap-based lane assignment.
- SQLite connections close immediately after transactions, including failures.

## Install or update

Extract the source archive and run `python3 installieren.py`. Add `--with-widget` for a new optional Plasma widget. Existing widgets are updated automatically; reload an active widget when convenient to use the corrected completion behavior. Quit the app with Ctrl+Q before restarting it after the update.

The installer downloads pinned Qt dependencies from PyPI. Event data and existing stored completion states are not automatically migrated or rewritten. This release introduces no new database format. See README.md, KNOWN_ISSUES.md and TESTING.md.

Regression checks use synthetic, isolated data. The fresh-account installation test remains excluded at the maintainer's request.

## Verification

60 Python tests, six JavaScript suites and real QML regression interactions pass. [Hosted release checks passed on Python 3.10, 3.12 and 3.14](https://github.com/jonas101201/liquid-calendar/actions/runs/40712199654). See [TESTING.md](TESTING.md) for the exact scope.
