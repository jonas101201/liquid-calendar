# 0.3.9.1 release record

Release date: **29 October 2026**. Beta prerelease, version **0.3.9.1**.

[Release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.9.1) · [Release notes](../RELEASE_NOTES.md) · [Follow-up audit](BUG_AUDIT_0.3.9_FOLLOWUP.md).

The patch adds held-pointer dragging to the Calendar Month/Week selector, opens the selected occurrence from month cards and displays overnight continuations with source-date editing/completion. Separate Series editing, future repeats, Undo, click/Space activation and reduced motion are preserved. No calendar-record migration; sharing protocol remains 3.

Validation: 144 Python tests, eight JavaScript suites, actual native QML pointer/keyboard/card interactions, isolated widget editing, source-copy synchronization, smoke launch and archive checksum/manifest checks. Independent Qt tests cover held LeftButton events, boundaries and cancellation, and real Open/Series/completion clicks on overnight repeated tasks. Hosted checks are attached to the release commit. Installation in a fresh user account has not been tested.

Earlier release tags and archives remain unchanged.
