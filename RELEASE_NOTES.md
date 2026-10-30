# Liquid Calendar 0.3.9.1

Beta prerelease · **29 October 2026**. [Release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.9.1).

## Calendar interaction fixes

- **Drag Month/Week:** hold the selected glass segment and drag it between Month and Week. The indicator follows the pointer and snaps on release. Clicks and Space activation remain available; hiding the control cancels the gesture. Reduced motion is respected.
- **Edit the selected occurrence:** Open in the month view now opens the displayed repeating occurrence, matching Today and Week. A separate Series action opens the whole series.
- **Show overnight continuations:** month/widget calendars display the following-day segment as Continued, with its remaining duration. Editing and task completion use the original occurrence date. Exact-midnight endings, all-day entries and cancelled occurrences do not create a continuation.

## Validation and update

144 Python tests, all eight JavaScript suites, actual native QML interactions, isolated widget editor checks, source synchronization and smoke launch checks passed. Independent Qt checks verified held-button drag, reverse movement, bounds, cancellation, keyboard activation and real month-card Open/Series/completion clicks. Repeating overnight tasks retain future occurrences, and Undo restores the original series. See the [follow-up audit](docs/BUG_AUDIT_0.3.9_FOLLOWUP.md).

Extract a release archive and run `python3 installieren.py`. Fully quit with **Ctrl+Q** before reopening; reload an active Plasma widget after updating shared files. No calendar-record migration is performed and sharing protocol stays at 3. Offscreen checks do not establish that all desktop environments are bug-free; installation in a fresh user account has not been tested.

[Known issues](KNOWN_ISSUES.md) · [Roadmap](ROADMAP.md).
