# 0.2.0-beta.1 release record

Release date: **28 October 2026**. The maintainer requested immediate publication, bringing forward the original 29 October target.

[Release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.2.0-beta.1) · [Release notes](../RELEASE_NOTES.md) · [Known issues](../KNOWN_ISSUES.md)

## Verified scope

- Optional no/low/medium/high task priorities, sorting and combined filters.
- Editable checklists with inline progress and independent recurring occurrences.
- Projects: assignment, combined filtering, sorting, completed/total counts, rename/merge/clear and Undo.
- Cross-date project/checklist search, JSON preservation and matching widget validation/editor.
- 77 Python tests, seven JavaScript suites, actual offscreen QML keyboard/interactions and a temporary-database smoke launch.
- A separate agent reproduced the follow-up bugs and independently rechecked their corrections.
- Corrected app/widget program files installed locally with a backup; installed-app smoke check passed without opening personal calendar data.

## Audit and CI evidence

Audited feature snapshot: [`fee524e`](https://github.com/jonas101201/liquid-calendar/commit/fee524ee31f0de11a8d4efd3d2a8090c84de3346).

- [Passing preparation tests on Python 3.10, 3.12 and 3.14](https://github.com/jonas101201/liquid-calendar/actions/runs/40734583186)
- [Passing preparation security analysis](https://github.com/jonas101201/liquid-calendar/actions/runs/40734571556)
- [Preparation pull request](https://github.com/jonas101201/liquid-calendar/pull/1)
- [Five-issue audit and regression evidence](BUG_AUDIT_0.2.0.md)

Resolved: stale project filters after Undo, quadratic project summaries, mismatched Unicode limits, inline checklists collapsing after each click, and partial project renames during concurrent edits. The earlier typed-step input correction is included too.

The final release tag identifies the source snapshot used to build the TAR and ZIP archives. GitHub shows final checks on that commit, along with the published assets and their digests. SHA256SUMS covers the two custom source archives; each archive also contains MANIFEST.sha256. Published tags and downloads must not be replaced to conceal later changes.

## Compatibility and validation limits

Existing entries need no migration. New fields are optional. Shared app/widget protocol remains 2. Project counts refer to stored records, not future recurring occurrences. Marking checklist steps does not automatically complete the parent task.

This is a targeted audit, not a guarantee of bug-free software. Long-term everyday usage, live desktop reminder delivery and complete installation behavior are not fully validated. The fresh-account installation test remains excluded. Existing platform, reminder and synchronization limitations in KNOWN_ISSUES.md remain applicable.
