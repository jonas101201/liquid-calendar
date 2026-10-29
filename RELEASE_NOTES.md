# Liquid Calendar 0.3.8.1

Released **28 October 2026** as a **beta prerelease**, version **0.3.8.1**. [Release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.8.1). The 0.3.8-beta.1 preparation was not published separately.

This maintenance patch shares identical editor/picker controls, centralizes standalone-widget source synchronization, replaces wildcard Python imports and reuses the existing occurrence-draft helper for task completion, checklist edits and moves. It introduces no visual redesign, new feature or database migration.

Verification uses the existing regression suites, distribution checks, actual Qt interactions and synthetic before/after renders. See the [refactor record](docs/REFACTOR_0.3.8.md). 133 Python tests, eight JavaScript suites, actual app/widget Qt checks, distribution checks and smoke launches passed. Eight of nine controlled before/after renders were pixel-identical; the week differed only in the animated scrollbar band, with identical content. Final hosted checks are recorded on the tagged commit. Installation in a fresh user account has not been tested.

Install/update: extract the archive and run `python3 installieren.py`. Fully quit with **Ctrl+Q** before reopening and reload an active widget to load the shared components. Existing calendar records are not migrated or rewritten. Sharing protocol remains 3. See the [release record](docs/RELEASE_0.3.8.1.md).
