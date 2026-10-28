# 0.2.0-beta.1 release preparation

Target: **29 October 2026, 12:00 Europe/Berlin (11:00 UTC)**.
Branch: `prepare/0.2.0-beta.1`. Public release: not published yet.

## Scope

- [x] Optional no/low/medium/high task priority, sorting and combined filters.
- [x] Editable checklists with inline progress and independent recurring occurrences.
- [x] Projects: assignment, combined filtering, sorting, completed/total counts, rename/merge/clear and Undo.
- [x] Cross-date project/checklist search, JSON preservation and matching widget validation/editor.
- [x] Updated VERSION, widget metadata, English documentation and synthetic screenshots.
- [x] Local Python, JavaScript, real offscreen QML and smoke checks.
- [ ] Hosted CI passed for the final release commit.
- [ ] Final publication metadata updated and source archives rebuilt from the exact release commit.
- [ ] Tag, GitHub prerelease and three matching assets published and verified.

## Publication procedure

1. At the scheduled time, inspect the preparation branch, working tree and CI. Preserve unrelated work and do not publish failed checks. Run the checks in TESTING.md on synthetic isolated data only. Do not perform a fresh-account installation test or change personal calendar data.
2. Ensure VERSION and widget metadata both say `0.2.0-beta.1`. Review the diff against main and resolve any newly introduced regressions before release.
3. Update README's preparation banner and download links to the new version; mark 0.2.0 released in ROADMAP, date CHANGELOG as 2026-10-29, remove the preparation wording in RELEASE_NOTES/KNOWN_ISSUES/TESTING, update CONTRIBUTING and the issue template's current public version, and update PUBLISHING with the new release link. Record actual verification evidence; do not claim live desktop or installation tests that were not run.
4. Commit those publication changes, fast-forward or merge the reviewed preparation into main, and require successful CI on that final commit. Build source archives with `python3 scripts/build_release.py` from that clean exact commit. Verify archive manifests and SHA256SUMS. Do not package the workspace, runtime, logs, personal databases or backups.
5. Create `v0.2.0-beta.1` on the final commit, then **Liquid Calendar 0.2.0 Beta 1**, marked prerelease. Attach `liquid-calendar-0.2.0-beta.1.tar.gz`, `liquid-calendar-0.2.0-beta.1.zip` and `SHA256SUMS`; use the matching RELEASE_NOTES.md. GitHub connector cannot create releases: use authenticated GitHub CLI if available, otherwise the signed-in browser. Never overwrite an existing tag or release.
6. Verify the public release, commit, prerelease status, asset names/checksums and links, then report the release URL and disable the once-only follow-up. If blocked, report the exact cause instead of claiming publication.

## Compatibility and limits

Existing entries need no migration. New fields are optional. Shared app/widget protocol remains 2. Project counts refer to stored records, not future recurring occurrences. Marking checklist steps does not automatically complete the parent task. All reminders, platform and validation limitations in KNOWN_ISSUES.md remain applicable.
