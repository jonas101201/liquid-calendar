# 0.3.8.1 release record

Release date: **28 October 2026**. Beta prerelease, version **0.3.8.1**. The 0.3.8-beta.1 development label was not published separately.

[Release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.8.1) · [Release notes](../RELEASE_NOTES.md) · [Known issues](../KNOWN_ISSUES.md)

## Included cleanup

- Common palette-driven text fields, checkboxes and number controls replace repeated editor/picker implementations.
- qml/ is canonical for eight shared files; a sync command maintains independently deployable widget copies. CI, package building and installation reject drift.
- Task completion, checklist updates and moves reuse the existing occurrence-draft helper, preserving original fingerprints and existing storage/Undo behavior.
- Python logic imports are explicit and Bridge initialization is easier to read.

No visual redesign, feature addition, database format change or personal-data migration. See [the refactor record](REFACTOR_0.3.8.md).

## Verification

133 Python tests, eight JavaScript suites, actual app and isolated-widget Qt interactions, shared-source distribution checks, both archive manifests and extracted-source smoke launches passed. Eight of nine controlled synthetic renders were pixel-identical; the week content was identical with differences only in the animated six-pixel scrollbar band. Installation in a fresh user account has not been tested. Final hosted tests and security analysis are attached to the tagged commit.

ZIP/TAR are built from the exact tagged source with the source allowlist. SHA256SUMS covers both, and each contains MANIFEST.sha256. Personal databases, backups and runtime dependencies are excluded. Previous public tags/assets remain unchanged.

## Updating

Quit with Ctrl+Q before reopening. Reload the active widget to load its copied shared components. Existing events are not rewritten. Sharing protocol remains 3; platform and feature limits remain documented in KNOWN_ISSUES.md.
