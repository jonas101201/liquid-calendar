# 0.2.0-beta.1 release preparation

Target: **29 October 2026, 12:00 Europe/Berlin (11:00 UTC)**.
Branch: `prepare/0.2.0-beta.1`. Public release: not published yet.

## Scope

- [x] Optional no/low/medium/high task priority, sorting and combined filters.
- [x] Editable checklists with inline progress and independent recurring occurrences.
- [x] Projects: assignment, combined filtering, sorting, completed/total counts, rename/merge/clear and Undo.
- [x] Cross-date project/checklist search, JSON preservation and matching widget validation/editor.
- [x] Updated VERSION, widget metadata, English documentation and synthetic screenshots.
- [x] 77 Python tests, seven JavaScript suites, real offscreen QML keyboard/interactions and a temporary-database smoke launch.
- [x] Follow-up bug fixes independently reproduced and rechecked by a separate agent.
- [x] Preparation CI passed on Python 3.10, 3.12 and 3.14; CodeQL completed successfully.
- [x] Corrected app/widget program files installed locally with a backup; installed-app smoke check passed without opening personal calendar data.
- [x] Preparation archives built and their source manifest verified; final release archives still need rebuilding after publication metadata changes.
- [ ] Hosted CI passed for the final release commit.
- [ ] Final publication metadata updated and source archives rebuilt from the exact release commit.
- [ ] Tag, GitHub prerelease and three matching assets published and verified.

## Verified preparation snapshot

Code reviewed: [`fee524e`](https://github.com/jonas101201/liquid-calendar/commit/fee524ee31f0de11a8d4efd3d2a8090c84de3346).

- [Successful preparation test run](https://github.com/jonas101201/liquid-calendar/actions/runs/40734583186)
- [Successful security analysis](https://github.com/jonas101201/liquid-calendar/actions/runs/40734571556)
- [Preparation pull request](https://github.com/jonas101201/liquid-calendar/pull/1)
- [Five-issue audit and regression evidence](https://github.com/jonas101201/liquid-calendar/blob/fee524ee31f0de11a8d4efd3d2a8090c84de3346/docs/BUG_AUDIT_0.2.0.md)

Resolved: stale project filters after Undo, quadratic project summaries, mismatched Unicode limits, inline checklists collapsing after each click, and partial project renames during concurrent edits. The earlier typed-step input correction is included too. See [release notes](https://github.com/jonas101201/liquid-calendar/blob/prepare/0.2.0-beta.1/RELEASE_NOTES.md) and [testing scope](https://github.com/jonas101201/liquid-calendar/blob/prepare/0.2.0-beta.1/TESTING.md).

The feature and audit work is complete for this preparation. The remaining unchecked items are publication steps, not additional feature promises. This does not establish that the beta is free of bugs. Long-term everyday usage, live desktop reminder delivery and complete installation behavior are not fully validated; the fresh-account installation test remains excluded.

## Publication procedure

1. At the scheduled time, inspect the preparation branch, working tree and CI. Preserve unrelated work and do not publish failed checks. Run the checks in TESTING.md on synthetic isolated data only. Do not perform a fresh-account installation test or change personal calendar data.
2. Ensure VERSION and widget metadata both say `0.2.0-beta.1`. Review the diff against main and resolve any newly introduced regressions before release.
3. Update README's preparation banner and download links to the new version; mark 0.2.0 released in ROADMAP, date CHANGELOG as 2026-10-29, remove the preparation wording in RELEASE_NOTES/KNOWN_ISSUES/TESTING, update CONTRIBUTING and the issue template's current public version, and update PUBLISHING with the new release link. Record actual verification evidence; do not claim live desktop or installation tests that were not run.
4. Commit those publication changes, fast-forward or merge the reviewed preparation into main, and require successful CI on that final commit. Build source archives with `python3 scripts/build_release.py` from that clean exact commit. Verify archive manifests and SHA256SUMS. Do not package the workspace, runtime, logs, personal databases or backups.
5. Create `v0.2.0-beta.1` on the final commit, then **Liquid Calendar 0.2.0 Beta 1**, marked prerelease. Attach `liquid-calendar-0.2.0-beta.1.tar.gz`, `liquid-calendar-0.2.0-beta.1.zip` and `SHA256SUMS`; use the matching RELEASE_NOTES.md. GitHub connector cannot create releases: use authenticated GitHub CLI if available, otherwise the signed-in browser. Never overwrite an existing tag or release.
6. Verify the public release, commit, prerelease status, asset names/checksums and links, then report the release URL and disable the once-only follow-up. If blocked, report the exact cause instead of claiming publication.

## Compatibility and limits

Existing entries need no migration. New fields are optional. Shared app/widget protocol remains 2. Project counts refer to stored records, not future recurring occurrences. Marking checklist steps does not automatically complete the parent task. All reminders, platform and validation limitations in KNOWN_ISSUES.md remain applicable.
