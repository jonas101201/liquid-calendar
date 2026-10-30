# 0.3.9.2 Beta 2 release record

Version: **0.3.9.2-beta.2** · Title: **Liquid Calendar 0.3.9.2 Beta 2** · **30 October 2026**.

[Release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.9.2-beta.2) · [Release notes](../RELEASE_NOTES.md).

Publishes the [0.3.9.2 source corrections](RELEASE_0.3.9.2.md) and the first separate Flatpak beta. The earlier merge/display implementation incorrectly combined independent contents or flagged intentional related events as conflicts; inner cards could cover the outer title. Independent linked records, contained cards in one outer lane, selective conflict detection and cleaner styling replace it. Previously destructive merges cannot be reconstructed automatically.

The Flatpak has its own storage by default, a separate desktop entry, asynchronous Notification/Background portals and shared KDE runtime dependencies. JSON can transfer existing events/tasks; template transfer and optional host-widget sharing have separate limits. See the [Flatpak guide](../flatpak/README.md).

Validation: 176 Python regressions pass natively and in the sandbox, eight JavaScript suites, actual native/Flatpak QML interactions, nested-card geometry and edit targets in both themes, isolated widget editing, private D-Bus portal requests, AppStream validation, shared-source checks, smoke launches and artifact checksums. Real login/file-picker acceptance and installation in a fresh user account have not been tested. Remaining native reminder issues are documented in [Known issues](../KNOWN_ISSUES.md).

The source archives and Flatpak identify the same versioned source snapshot. Existing published tags/assets are not moved or replaced. The original 0.3.9.2 label was a source-only repository update, not a separate packaged release.
