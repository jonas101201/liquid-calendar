# Liquid Calendar 0.3.9.5

Beta bug-fix prerelease · **9 November 2026** · [Downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.9.5).

## Fixed

- Native reminders titled `--help` or beginning with `-` are delivered as text instead of being interpreted as command options.
- Slow native notification delivery no longer blocks the calendar interface. Delivery runs asynchronously, one attempt at a time, with an eight-second timeout.
- A reminder is marked delivered only after a successful process exit. Failed starts, nonzero exits and timeouts remain retryable without duplicate pending attempts. Pausing reminders discards the native queue; quitting stops child processes.

The two reminder defects documented in 0.3.9.4 are now marked fixed in [Known Issues](KNOWN_ISSUES.md). Flatpak keeps its asynchronous portal backend. All 0.3.9.4 task files and calendar polish features are retained.

## Validation and scope

218 Python tests, nine JavaScript suites and isolated real Qt interactions cover the change and existing calendar, attachments, import/cancellation and widget behavior. Real child processes verify timeout, queue, retry/cancellation and event-loop responsiveness. Hosted checks are associated with the release source commit. See [the audit](docs/BUG_AUDIT_0.3.9.5.md).

Fedora/KDE Plasma is the target. Real notification-daemon acceptance, interactive host file pickers/viewers, login/autostart prompts, live Plasma reload and fresh-account installation are not established by isolated checks. Reminders require the app to remain running. Existing published tags/downloads remain unchanged.

Source ZIP/TAR archives and a separate x86_64 Flatpak bundle are supplied with SHA256SUMS and a Flatpak build receipt. The Flatpak is a GitHub beta bundle, not a Flathub listing.
