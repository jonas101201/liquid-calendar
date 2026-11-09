# 0.3.9.5 release record

**Liquid Calendar 0.3.9.5** · Beta prerelease · **9 November 2026** · Tag `v0.3.9.5`.

[Release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.9.5) · [Release notes](../RELEASE_NOTES.md) · [Known issues](../KNOWN_ISSUES.md).

Fixes native reminder argument handling and UI blocking, with asynchronous queue/completion, timeout/retry tracking, pause cancellation and shutdown cleanup. See [the audit](BUG_AUDIT_0.3.9.5.md).

Validation: 218 Python tests, nine JavaScript suites, isolated real QML interactions in both themes, portal and widget checks, native/Flatpak smoke checks, source synchronization, AppStream validation and matching archive/bundle checksums. Real child processes verify literal arguments, responsiveness, failure, timeout and queue lifecycle. Hosted checks identify the release source commit.

Real desktop notification display, interactive host pickers/viewers, login/autostart prompts, live Plasma reload and fresh-account installation are not established by automated checks. Earlier tags and published downloads remain unchanged. The source archives and Flatpak receipt identify the same versioned source payload.
