# Liquid Calendar 0.3.7 Beta 1

Released **28 October 2026**. [Release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.7-beta.1). Bug-fix prerelease for 0.3.6; English interface, Fedora/KDE Plasma, GPL-3.0-or-later.

- Exact date searches no longer substitute another occurrence for a cancelled date; undated text matches are excluded from exact calendar-day queries.
- Time suggestions account for elapsed seconds rather than offering an interval that already began.
- Scheduling checks availability inside the write transaction, so a concurrent booking causes a conflict instead of a double booking.
- Recurrence scans, week headers, drop targets and navigation handle the supported date endpoints safely.

The patch does not migrate or rewrite existing calendar records. Source and companion-widget versions match. Tests and review use isolated synthetic records; fresh-account installation remains excluded. See the [audit record](docs/BUG_AUDIT_0.3.7.md), [testing scope](TESTING.md) and [known issues](KNOWN_ISSUES.md).

Verification: 131 Python tests, eight JavaScript suites, actual Qt interaction/render checks, isolated widget editing and temporary-database smoke launches passed locally. An independent agent reviewed the initial fixes, reproduced additional bugs, and re-reviewed the corrections. Final hosted checks are attached to the tagged release commit. This is scoped verification, not a guarantee of universal bug freedom.

Install/update: extract the archive and run `python3 installieren.py`. Fully quit with **Ctrl+Q** before reopening; reload an active companion widget to load the corrected JavaScript. Sharing protocol remains 3. See the [release record](docs/RELEASE_0.3.7.md).
