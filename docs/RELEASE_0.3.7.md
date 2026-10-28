# 0.3.7-beta.1 release record

Release date: **28 October 2026**, at the maintainer's request.

[Release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.7-beta.1) · [Release notes](../RELEASE_NOTES.md) · [Known issues](../KNOWN_ISSUES.md)

## Bug fixes

- Exact ISO/DMY and relative-day searches require actual occurrences on the requested day in Python and app/widget JavaScript.
- Planning suggestions and final validation account for elapsed seconds/microseconds.
- Task scheduling checks latest availability inside the write transaction, rejecting a competing booking inserted after the preliminary check.
- Recurrence scans, week headers, unavailable drop targets and navigation respect supported date endpoints.

## Verification

131 Python tests, eight JavaScript suites, actual Qt interaction/render checks including date endpoints, isolated widget editor and temporary-database smoke launches passed. A separate read-only agent verified initial corrections, reproduced additional bugs, and re-reviewed the final fixes. See [the audit record](BUG_AUDIT_0.3.7.md). Final hosted tests and security analysis are attached to the tagged commit. Tests use synthetic data only; fresh-account installation remains excluded. This is targeted verification, not a guarantee of universal bug freedom.

ZIP and TAR are built from the exact tagged source commit using the source allowlist. SHA256SUMS covers both archives; each archive includes MANIFEST.sha256. Personal databases, backups and runtime dependencies are excluded. Existing published tags/assets are never replaced.

## Updating

Quit the app fully with Ctrl+Q before reopening. Reload the active widget to load its corrected JavaScript. Sharing protocol stays 3, and existing records are not automatically migrated or rewritten. Platform/language/feature limitations remain documented in [KNOWN_ISSUES.md](../KNOWN_ISSUES.md).
