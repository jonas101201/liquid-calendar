# 0.3.9 release record

Release date: **29 October 2026**. Beta prerelease, version **0.3.9**.

[Release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.9) · [Release notes](../RELEASE_NOTES.md) · [UI audit](UI_AUDIT_2026-10-29.md).

This release contains the consolidated Calendar navigation, adaptive Liquid Glass palette and theme previews, UI motion, directly draggable scrollbars, frozen week time labels, lightweight opacity preview and draft-aware event merging. Concurrent merge sources are verified inside the SQLite transaction. Calendar data is not migrated and sharing protocol remains 3.

Local checks: 144 Python tests; eight JavaScript suites; actual native QML interactions; isolated widget editing; temporary-database smoke launch; source-copy synchronization; ten light/dark accent renders; opacity stress with 1,000 synthetic events; package checksums and archive manifests. Hosted checks are available on the release commit. Independent reviews covered the UI, unsaved merge values, Undo and concurrent merges. Installation in a fresh user account has not been tested.

ZIP and TAR source packages include a MANIFEST.sha256; SHA256SUMS checks both archives. Published earlier tags and archives remain unchanged.
