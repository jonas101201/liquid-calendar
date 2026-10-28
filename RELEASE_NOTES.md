# Liquid Calendar 0.3.7 Beta 1 — preparation

Not published. Current public release: [0.3.6-beta.1](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.6-beta.1).

- Exact date searches no longer substitute another occurrence for a cancelled date; undated text matches are excluded from exact calendar-day queries.
- Time suggestions account for elapsed seconds rather than offering an interval that already began.
- Scheduling checks availability inside the write transaction, so a concurrent booking causes a conflict instead of a double booking.
- Recurrence scans, week headers, drop targets and navigation handle the supported date endpoints safely.

The patch does not migrate or rewrite existing calendar records. Source and companion-widget versions match. Tests and review use isolated synthetic records; fresh-account installation remains excluded. See the [audit record](docs/BUG_AUDIT_0.3.7.md), [testing scope](TESTING.md) and [known issues](KNOWN_ISSUES.md). No new release has been published.
